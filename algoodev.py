import random
import time
import math
import matplotlib.pyplot as plt


# YARDIMCI FONKSİYONLAR

def oryantasyon(n1, n2, n3):
    """
    n1 → n2 doğrusu referans alındığında n3 noktasının
    bu doğruya göre hangi tarafta kaldığını belirlemek.

    > 0  : Saat yönü tersine dönüş (kabul)
    < 0  : Saat yönüne dönüş 
    = 0  : Üç nokta doğrusal
    """
    return (n2[0] - n1[0]) * (n3[1] - n1[1]) - \
           (n2[1] - n1[1]) * (n3[0] - n1[0])

def rastgele_nokta_uret(n):
    """
    [0,1000] aralığında rastgele (x,y) koordinatlarından oluşan
    n adet nokta üretir.
    """
    return [(random.randint(0, 1000), random.randint(0, 1000)) for _ in range(n)]


def kaba_kuvvet_kapali_cevrim(noktalar):
    """
    Brute Force (Kaba Kuvvet) Convex Hull algoritması.
    Her iki nokta çifti (p,q) için,
    diğer tüm noktaların bu doğruya göre
    tek bir tarafta kalıp kalmadığı kontrol edilir.

    Eğer tüm noktalar aynı taraftaysa:
    → (p,q) Convex Hull’un bir kenarıdır.

    Zaman karmaşıklığı:
    - Üç iç içe döngü → O(N³)
    """
    n = len(noktalar) #nokta sayısı hesaplanır
    kenarlar = [] #kenar adayları burada saklanır 

    # Tüm nokta çiftleri (p,g) oluşturulur 
    for i in range(n):   #O(N)
        for j in range(i + 1, n): #aynı çiftin tersi tekrarını önelemk için i+1 den başlanır #O(N)
            p, q = noktalar[i], noktalar[j] #kenar adayı oluşturulur
            sol = sag = False

            # Diğer tüm noktaların (p,q) doğrusuna göre konumunu kontrol et
            for k in range(n):   #O(N)
                r = noktalar[k] #kontrol edilen üçüncü nokta
                d = oryantasyon(p, q, r) #r nin (p,q) doğrusuna göre sağ sol üzeri hiza hesabı

                # Nokta sol taraftaysa
                if d > 0:   #O(1)
                    sol = True
                # Nokta sağ taraftaysa
                elif d < 0:
                    sag = True

                if sag and sol:
                    break


            # Noktaların tamamı tek taraftaysa
            if not (sol and sag): #O(N^2)
                kenarlar.append((p, q)) #convex hull kenarı kabul edilir
    
    # Hiç kenar bulunamazsa boş döndür
    if not kenarlar:  #O(1)
        return []

    # Convex Hull’a ait benzersiz noktalar kümesi.
    # set ile aynı nokta tekrarı engellenir list ile listelenir
    hull_noktalari = list(set([p for e in kenarlar for p in e]))

    # Merkez noktayı hesapla (saat yönünde sıralama için) O(N)
    merkez_x = sum(p[0] for p in hull_noktalari) / len(hull_noktalari)
    merkez_y = sum(p[1] for p in hull_noktalari) / len(hull_noktalari)

    # Noktaları merkeze göre açısal olarak sırala O(N LOG N)  0(N^3) yanında ihmal edilir.
    hull_noktalari.sort(
        key=lambda p: math.atan2(p[1] - merkez_y, p[0] - merkez_x)
    )

    return hull_noktalari

def graham_scan_kapali_cevrim(noktalar):
    """
    Graham Scan Convex Hull algoritması.
    1) En alt (y, sonra x) noktayı başlangıç noktası seç
    2) Diğer noktaları bu noktaya göre açısal sırala
    3) Stack (yığın) kullanarak sağ dönüşleri ele

    Zaman karmaşıklığı:
    - Sıralama: O(N log N)
    - Tarama: O(N)
    - Toplam: O(N log N)
    """
    if len(noktalar) < 3: #en az 3 nokta varsa zaten hull oluşmuştur
        return noktalar

    # En düşük y (eşitse en düşük x) koordinatlı nokta seçilir 
    baslangic = min(noktalar, key=lambda n: (n[1], n[0]))   #O(N)

    # Noktaları başlangıca göre polar açıya göre sırala
    sirali = sorted(            #O(N LOG N)
        noktalar,
        key=lambda n: (         # N x O(1)= O(N)
            math.atan2(n[1] - baslangic[1], n[0] - baslangic[0]), # bslngç ->n vektörünün x ile yaptığı açı hesaplanır
            (n[0] - baslangic[0])**2 + (n[1] - baslangic[1])**2  #aynı açıyı paylaşan noktalar varsa bşlngc yakın olan önce gelir
        )
    )

    yigin = []

    # Sıralı noktalar üzerinden convex hull inşası
    for n in sirali:   #O(N)
        # Sağ dönüş veya doğrusal durum varsa
        # yığından çıkar (convexliği bozuyor)
        while len(yigin) >= 2 and oryantasyon(yigin[-2], yigin[-1], n) <= 0: 
            yigin.pop()  #bozan son nokta çıkarılır (sol dönüşe kadar)
        yigin.append(n)  #yeni nokta dahil edilir (sol dönüşte)

    return yigin # noktalar saat yönü tersine sıralı yığında 

# GÖRSELLEŞTİRME FONKSİYONU
def cizim_yap(noktalar, hull, baslik, renk):
    """
    Noktaları ve Convex Hull sınırını matplotlib ile çizer.
    """

    # Grafik penceresi
    plt.figure(figsize=(7, 6))

    # Tüm noktaları çiz
    x, y = zip(*noktalar)
    # Noktalar dağılım grafiği (s nokta büyüklüğü) 
    plt.scatter(x, y, s=20)

    # Convex Hull varsa kapalı çevrim çiz
    if hull:
        hull_cizim = hull + [hull[0]] #ilk nokta kapamak için sona eklenir
        hx, hy = zip(*hull_cizim)
        plt.plot(hx, hy, color=renk, linewidth=2) #hull sınır çizgileri

    plt.title(baslik)
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.grid(True) #klavuz çizgileri arkada görünsün
    plt.show() #grafiği göster


# PERFORMANS TESTİ VE ANA AKIŞ
def performans_testi():
    """
    1) Küçük veri kümesiyle görsel doğrulama
    2) Artan N değerleri için zaman ölçümü
    3) Brute Force ve Graham Scan karşılaştırması
    """

    # --- 1. ADIM: GÖRSEL ÇIKTILAR ---
    print("Görselleştirmeler hazırlanıyor...")
    ornek_noktalar = rastgele_nokta_uret(100)

    #Brute Force algoritması çağrılır.
    bf_hull = kaba_kuvvet_kapali_cevrim(ornek_noktalar)
    cizim_yap(ornek_noktalar, bf_hull, "Brute Force Convex Hull", "red")

    #Graham Scan algoritması çalıştırılır.
    gs_hull = graham_scan_kapali_cevrim(ornek_noktalar)
    cizim_yap(ornek_noktalar, gs_hull, "Graham Scan Convex Hull", "green")

    # --- 2. ADIM: PERFORMANS ANALİZİ ---
    TIME_LIMIT = 10.0      # Pratik üst süre sınırı (saniye)
    N = 100               # Başlangıç nokta sayısı
    STEP = 100            # Artış miktarı

    #Ölçüm Sonuçlarını Saklayacak Listeler
    nokta_sayilari, kaba_ms, graham_ms = [], [], []

    print("\n--- Algoritma Performans Karşılaştırması ---")
    print(f"{'N':<10} | {'Brute Force (sn)':<20} | {'Graham Scan (sn)':<20}")
    print("-" * 55)

    while True:
        noktalar = rastgele_nokta_uret(N)

        # Brute Force süre ölçümü
        bas_bf = time.perf_counter() #zaman ölçümü başlatılır
        kaba_kuvvet_kapali_cevrim(noktalar) #brute force algoritması çağırılır
        sure_kaba = time.perf_counter() - bas_bf #toplam çalışma süresi hesaplanır

        # Graham Scan süre ölçümü
        bas_gs = time.perf_counter()
        graham_scan_kapali_cevrim(noktalar)
        sure_graham = time.perf_counter() - bas_gs

        # Anlık sonuçları yazdır
        print(f"{N:<10} | {sure_kaba:<20.6f} | {sure_graham:<20.6f}")

        nokta_sayilari.append(N) #x ekseni için nokta sayıları kaydedilir
        kaba_ms.append(sure_kaba * 1000) #süreler milisaniyeye çevrilir
        graham_ms.append(sure_graham * 1000)

        # Brute Force pratik sınırı aşarsa durdur
        if sure_kaba > TIME_LIMIT:
            print("\n" + "!" * 40)
            print(f"Brute Force algoritması N = {N} değerinden itibaren")
            print(f"{TIME_LIMIT:.1f} saniyeden uzun sürdüğü için durduruldu.")
            print("!" * 40)
            break

        N += STEP

    # --- 3. ADIM: KARŞILAŞTIRMA GRAFİĞİ ---
    plt.figure(figsize=(10, 6))
    plt.plot(nokta_sayilari, kaba_ms, marker="o", label="Kaba Kuvvet (O(N³))") #Brute force süreleri çizilir
    plt.plot(nokta_sayilari, graham_ms, marker="s", label="Graham Scan (O(N log N))") #Graham Scan sonuçları çizilir.
    plt.axhline(y=TIME_LIMIT * 1000, linestyle="--", label="Pratik Süre Sınırı (3000 ms)") #Pratik süre sınırı yatay çizgiyle gösterilir.
    plt.yscale("log") #değerlerin minimal değişimlerini görmek adına kullanılmıştır.
    plt.xlabel("N (Nokta Sayısı)")
    plt.ylabel("Çalışma Süresi (ms)")
    plt.title("Convex Hull Performans Karşılaştırması")
    plt.legend() # açıklama kutusu 
    plt.grid(True) #ızgara
    plt.show()  #grafik gösterim

if __name__ == "__main__":
    performans_testi()
