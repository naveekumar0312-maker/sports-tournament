from django.core.management.base import BaseCommand
from locations.models import District, Taluk, Village

class Command(BaseCommand):
    help = 'Seeds all 38 Tamil Nadu Districts, Taluks, and Villages'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Seeding all 38 Tamil Nadu Districts, Taluks, and Villages...'))

        tn_districts_taluks = {
            "Ariyalur": ["Ariyalur", "Udayarpalayam", "Sendurai", "Andimadam"],
            "Chengalpattu": ["Chengalpattu", "Tambaram", "Pallavaram", "Vandalur", "Maduranthakam", "Cheyyur", "Thirukalukundram"],
            "Chennai": ["Mylapore", "Guindy", "Egmore", "T. Nagar", "Velachery", "Ambattur", "Aminjikarai", "Ayanavaram", "Mambalam", "Purasaivakkam", "Royapuram", "Perambur", "Sholinganallur", "Thiruvottiyur", "Tondiarpet"],
            "Coimbatore": ["Coimbatore North", "Coimbatore South", "Pollachi", "Mettupalayam", "Sulur", "Annur", "Kinathukadavu", "Valparai", "Perur"],
            "Cuddalore": ["Cuddalore", "Chidambaram", "Panruti", "Vriddhachalam", "Kurinjipadi", "Tittagudi", "Bhuvanagiri", "Veppur"],
            "Dharmapuri": ["Dharmapuri", "Harur", "Palacode", "Pennagaram", "Pappireddipatti", "Nallampalli", "Karimangalam"],
            "Dindigul": ["Dindigul East", "Dindigul West", "Palani", "Kodaikanal", "Nattam", "Nilakottai", "Oddanchatram", "Vedasandur", "Attur"],
            "Erode": ["Erode", "Perundurai", "Bhavani", "Gobichettipalayam", "Sathyamangalam", "Modakurichi", "Thalavadi", "Kodumudi"],
            "Kallakurichi": ["Kallakurichi", "Sankarapuram", "Tirukoilur", "Ulundurpet", "Chinnasalem", "Kalvarayan Hills"],
            "Kanchipuram": ["Kanchipuram", "Sriperumbudur", "Uthiramerur", "Walajabad", "Kundrathur"],
            "Kanyakumari": ["Agasteeswaram", "Thovalai", "Kalkulam", "Vilavancode", "Thiruvattar", "Killiyoor"],
            "Karur": ["Karur", "Kulithalai", "Aravakurichi", "Manmangalam", "Krishnarayapuram", "Pugalur"],
            "Krishnagiri": ["Krishnagiri", "Hosur", "Denkanikottai", "Pochampalli", "Uthangarai", "Bargur", "Anchatti", "Shoolagiri"],
            "Madurai": ["Madurai North", "Madurai South", "Melur", "Thiruparankundram", "Vadipatti", "Usilampatti", "Peraiyur", "Thirumangalam", "Kallikudi"],
            "Mayiladuthurai": ["Mayiladuthurai", "Sirkazhi", "Tharangambadi", "Kuthalam"],
            "Nagapattinam": ["Nagapattinam", "Kilvelur", "Vedaranyam", "Thirukkuvalai"],
            "Namakkal": ["Namakkal", "Rasipuram", "Tiruchengode", "Paramathi Velur", "Kolli Hills", "Senthamangalam", "Komarapalayam"],
            "Nilgiris": ["Udhagamandalam (Ooty)", "Coonoor", "Kotagiri", "Gudalur", "Pandalur", "Kundah"],
            "Perambalur": ["Perambalur", "Kunnam", "Veppanthattai", "Alathur"],
            "Pudukkottai": ["Pudukkottai", "Alangudi", "Aranthangi", "Illuppur", "Gandarvakottai", "Avadaiyarkoil", "Karambakudi", "Kulathur", "Ponnamaravathi", "Thirumayam"],
            "Ramanathapuram": ["Ramanathapuram", "Paramakudi", "Rameswaram", "Mudukulathur", "Tiruvadanai", "Kadaladi", "Kamuthi", "Kilakarai"],
            "Ranipet": ["Ranipet", "Walajah", "Arakkonam", "Sholinghur", "Kalavai", "Nemili"],
            "Salem": ["Salem North", "Salem South", "Attur", "Mettur", "Omalur", "Sankari", "Yercaud", "Edappadi", "Gangavalli", "Kadayampatti", "Salem West", "Valapady"],
            "Sivaganga": ["Sivaganga", "Karaikudi", "Devakottai", "Manamadurai", "Ilayangudi", "Kalaiyarkoil", "Tiruppattur"],
            "Tenkasi": ["Tenkasi", "Sankarankovil", "Kadayanallur", "Shenkottai", "Alangulam", "Sivagiri", "Thiruvengadam"],
            "Thanjavur": ["Thanjavur", "Kumbakonam", "Pattukkottai", "Orathanadu", "Papanasam", "Thiruvaiyaru", "Thirupanandal", "Peravurani"],
            "Theni": ["Theni", "Periyakulam", "Uthamapalayam", "Bodinayakanur", "Andipatti"],
            "Thoothukudi": ["Thoothukudi", "Tiruchendur", "Kovilpatti", "Ettayapuram", "Vilathikulam", "Sathankulam", "Eral", "Ottapidaram", "Srivaikuntam"],
            "Tiruchirappalli": ["Srirangam", "Trichy East", "Trichy West", "Lalgudi", "Manapparai", "Musiri", "Thottiyam", "Thuraiyur", "Manachanallur"],
            "Tirunelveli": ["Tirunelveli", "Palayamkottai", "Ambasamudram", "Nanguneri", "Radhapuram", "Cheranmahadevi"],
            "Tirupathur": ["Tirupathur", "Vaniyambadi", "Ambur", "Natrampalli"],
            "Tiruppur": ["Tiruppur North", "Tiruppur South", "Avinashi", "Dharapuram", "Kangeyam", "Udumalaipettai", "Madathukulam", "Palladam"],
            "Tiruvallur": ["Tiruvallur", "Avadi", "Ponneri", "Poonamallee", "Tiruttani", "Gummidipoondi", "Uthukkottai", "RK Pet"],
            "Tiruvannamalai": ["Tiruvannamalai", "Cheyyar", "Arani", "Chengam", "Polur", "Vandavasi", "Kalasapakam", "Jawadhu Hills"],
            "Tiruvarur": ["Tiruvarur", "Mannargudi", "Thiruthuraipoondi", "Nannilam", "Needamangalam", "Valangaiman", "Kudavasal"],
            "Vellore": ["Vellore", "Katpadi", "Gudiyatham", "Anaicut", "Pernambut"],
            "Viluppuram": ["Viluppuram", "Tindivanam", "Gingee", "Vanur", "Vikravandi", "Kandachipuram", "Marakkanam"],
            "Virudhunagar": ["Virudhunagar", "Sivakasi", "Rajapalayam", "Aruppukottai", "Sattur", "Srivilliputhur", "Tiruchuli", "Vembakottai"],
        }

        for d_name, taluk_list in tn_districts_taluks.items():
            dist_obj, _ = District.objects.get_or_create(
                name=d_name,
                defaults={'code': d_name[:3].upper()}
            )
            for t_name in taluk_list:
                taluk_obj, _ = Taluk.objects.get_or_create(name=t_name, district=dist_obj)
                
                # Seed villages for each taluk
                village_names = [f"{t_name} North Village", f"{t_name} South Village", f"{t_name} Central Village"]
                for v_name in village_names:
                    Village.objects.get_or_create(name=v_name, taluk=taluk_obj)

        total_d = District.objects.count()
        total_t = Taluk.objects.count()
        total_v = Village.objects.count()
        self.stdout.write(self.style.SUCCESS(f'Successfully seeded {total_d} Districts, {total_t} Taluks, and {total_v} Villages!'))

