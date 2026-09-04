import os
import re
import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, models
from locations.models import District, Taluk, Village

class Command(BaseCommand):
    help = 'Imports Tamil Nadu District, Taluk/SubDistrict, and Village data from an Excel or CSV file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel (.xlsx/.xls) or CSV (.csv) file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")

        self.stdout.write(self.style.NOTICE(f"Opening file: {file_path}"))

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, dtype=str)
            else:
                df = pd.read_excel(file_path, dtype=str)
        except Exception as e:
            raise CommandError(f"Failed to read file: {e}")

        # Clean column names for detection
        columns = list(df.columns)

        def normalize(col):
            return re.sub(r'[^a-z0-9]', '', str(col).lower())

        def find_col(candidates):
            # First try exact match
            for cand in candidates:
                n_cand = normalize(cand)
                for orig in columns:
                    if n_cand == normalize(orig):
                        return orig
            # Then try substring match
            for cand in candidates:
                n_cand = normalize(cand)
                for orig in columns:
                    if n_cand in normalize(orig):
                        return orig
            return None

        state_col = find_col(['state', 'statename', 'state_name'])
        district_col = find_col(['district', 'districtname', 'district_name'])
        district_lgd_col = find_col(['districtlgdcode', 'districtlgd', 'districtcode', 'district_lgd_code'])
        
        taluk_col = find_col(['subdistrict', 'subdistrictname', 'taluk', 'talukname', 'sub_district_name', 'subdistrict_name'])
        taluk_lgd_col = find_col(['subdistrictlgdcode', 'subdistrictlgd', 'taluklgdcode', 'sub_district_lgd_code'])
        
        village_col = find_col(['village', 'villagename', 'village_name'])
        village_lgd_col = find_col(['villagelgdcode', 'villagelgd', 'villagecode', 'village_lgd_code'])
        pin_col = find_col(['pincode', 'pin_code', 'pin'])


        self.stdout.write(f"Detected columns:")
        self.stdout.write(f"  State: {state_col}")
        self.stdout.write(f"  District: {district_col}")
        self.stdout.write(f"  District LGD: {district_lgd_col}")
        self.stdout.write(f"  Taluk: {taluk_col}")
        self.stdout.write(f"  Taluk LGD: {taluk_lgd_col}")
        self.stdout.write(f"  Village: {village_col}")
        self.stdout.write(f"  Village LGD: {village_lgd_col}")
        self.stdout.write(f"  PIN Code: {pin_col}")

        if not district_col:
            raise CommandError("Could not detect District column in file!")

        # Filter Tamil Nadu rows if State column exists
        if state_col:
            df = df[df[state_col].astype(str).str.contains('tamil|tn', case=False, na=False)]

        districts_processed = 0
        taluks_processed = 0
        villages_processed = 0

        created_d, updated_d = 0, 0
        created_t, updated_t = 0, 0
        created_v, updated_v = 0, 0

        skipped = 0
        errors = 0

        districts_cache = {}
        taluks_cache = {}

        self.stdout.write(self.style.NOTICE("Importing Tamil Nadu Location Hierarchy..."))

        for idx, row in df.iterrows():
            try:
                d_name = str(row.get(district_col, '')).strip() if district_col and pd.notna(row.get(district_col)) else ''
                d_lgd = str(row.get(district_lgd_col, '')).strip() if district_lgd_col and pd.notna(row.get(district_lgd_col)) else None
                
                t_name = str(row.get(taluk_col, '')).strip() if taluk_col and pd.notna(row.get(taluk_col)) else ''
                t_lgd = str(row.get(taluk_lgd_col, '')).strip() if taluk_lgd_col and pd.notna(row.get(taluk_lgd_col)) else None
                
                v_name = str(row.get(village_col, '')).strip() if village_col and pd.notna(row.get(village_col)) else ''
                v_lgd = str(row.get(village_lgd_col, '')).strip() if village_lgd_col and pd.notna(row.get(village_lgd_col)) else None
                pin = str(row.get(pin_col, '')).strip() if pin_col and pd.notna(row.get(pin_col)) else None

                if not d_name or d_name.lower() == 'nan':
                    skipped += 1
                    continue

                # Process District
                d_lgd_int = int(float(d_lgd)) if d_lgd and d_lgd.replace('.', '').isdigit() else None
                dist_key = d_lgd_int if d_lgd_int else d_name.upper()

                if dist_key not in districts_cache:
                    if d_lgd_int:
                        dist_obj, d_created = District.objects.update_or_create(
                            lgd_code=d_lgd_int,
                            defaults={'name': d_name, 'state_name': 'Tamil Nadu', 'is_active': True}
                        )
                    else:
                        dist_obj, d_created = District.objects.update_or_create(
                            name=d_name,
                            defaults={'state_name': 'Tamil Nadu', 'is_active': True}
                        )
                    districts_cache[dist_key] = dist_obj
                    districts_processed += 1
                    if d_created:
                        created_d += 1
                    else:
                        updated_d += 1
                else:
                    dist_obj = districts_cache[dist_key]

                # Process Taluk
                if not t_name or t_name.lower() == 'nan':
                    continue

                t_lgd_int = int(float(t_lgd)) if t_lgd and t_lgd.replace('.', '').isdigit() else None
                taluk_key = (dist_obj.id, t_lgd_int if t_lgd_int else t_name.upper())

                if taluk_key not in taluks_cache:
                    if t_lgd_int:
                        taluk_obj, t_created = Taluk.objects.update_or_create(
                            district=dist_obj,
                            lgd_code=t_lgd_int,
                            defaults={'name': t_name, 'is_active': True}
                        )
                    else:
                        taluk_obj, t_created = Taluk.objects.update_or_create(
                            district=dist_obj,
                            name=t_name,
                            defaults={'is_active': True}
                        )
                    taluks_cache[taluk_key] = taluk_obj
                    taluks_processed += 1
                    if t_created:
                        created_t += 1
                    else:
                        updated_t += 1
                else:
                    taluk_obj = taluks_cache[taluk_key]

                # Process Village
                if not v_name or v_name.lower() == 'nan':
                    continue

                v_lgd_int = int(float(v_lgd)) if v_lgd and v_lgd.replace('.', '').isdigit() else None

                if v_lgd_int:
                    village_obj, v_created = Village.objects.update_or_create(
                        taluk=taluk_obj,
                        lgd_code=v_lgd_int,
                        defaults={'name': v_name, 'pin_code': pin, 'is_active': True}
                    )
                else:
                    village_obj, v_created = Village.objects.update_or_create(
                        taluk=taluk_obj,
                        name=v_name,
                        defaults={'pin_code': pin, 'is_active': True}
                    )

                villages_processed += 1
                if v_created:
                    created_v += 1
                else:
                    updated_v += 1

            except Exception as e:
                errors += 1
                self.stderr.write(f"Error on row {idx}: {e}")

        # Summary output
        self.stdout.write(self.style.SUCCESS("""
Location Import Completed

State: Tamil Nadu

Districts processed: {dp}
Taluks processed: {tp}
Villages processed: {vp}

Created:
Districts: {cd}
Taluks: {ct}
Villages: {cv}

Updated:
Districts: {ud}
Taluks: {ut}
Villages: {uv}

Skipped:
{sk}

Errors:
{err}
""".format(
            dp=districts_processed, tp=taluks_processed, vp=villages_processed,
            cd=created_d, ct=created_t, cv=created_v,
            ud=updated_d, ut=updated_t, uv=updated_v,
            sk=skipped, err=errors
        )))

        # Automated Data Quality Check
        self.run_quality_check()

    def run_quality_check(self):
        self.stdout.write(self.style.NOTICE("\n--- DATA QUALITY CHECK REPORT ---"))

        # 1. Check duplicate District LGD codes
        dup_dist_lgd = District.objects.exclude(lgd_code__isnull=True).values('lgd_code').annotate(cnt=models.Count('id')).filter(cnt__gt=1)
        self.stdout.write(f"1. Duplicate District LGD codes: {dup_dist_lgd.count()}")

        # 2. Check duplicate Taluk LGD codes
        dup_taluk_lgd = Taluk.objects.exclude(lgd_code__isnull=True).values('district', 'lgd_code').annotate(cnt=models.Count('id')).filter(cnt__gt=1)
        self.stdout.write(f"2. Duplicate Taluk LGD codes: {dup_taluk_lgd.count()}")

        # 3. Check duplicate Village LGD codes
        dup_vil_lgd = Village.objects.exclude(lgd_code__isnull=True).values('taluk', 'lgd_code').annotate(cnt=models.Count('id')).filter(cnt__gt=1)
        self.stdout.write(f"3. Duplicate Village LGD codes: {dup_vil_lgd.count()}")

        # 4. Check villages without Taluk
        orphan_villages = Village.objects.filter(taluk__isnull=True).count()
        self.stdout.write(f"4. Villages without Taluk: {orphan_villages}")

        # 5. Check Taluks without District
        orphan_taluks = Taluk.objects.filter(district__isnull=True).count()
        self.stdout.write(f"5. Taluks without District: {orphan_taluks}")

        # 6. Check Districts without state
        empty_state = District.objects.filter(models.Q(state_name__isnull=True) | models.Q(state_name='')).count()
        self.stdout.write(f"6. Districts without State: {empty_state}")

        # 7. Check empty names
        empty_names = District.objects.filter(name='').count() + Taluk.objects.filter(name='').count() + Village.objects.filter(name='').count()
        self.stdout.write(f"7. Empty location names: {empty_names}")

        # 8. Check invalid Tamil Nadu records
        non_tn = District.objects.exclude(state_name__icontains='Tamil Nadu').count()
        self.stdout.write(f"8. Non-Tamil Nadu records: {non_tn}")

        self.stdout.write(self.style.SUCCESS("Data Quality Check Completed Successfully!"))
