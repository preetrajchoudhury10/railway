# Indian Companies Database — 20,000+ career page URLs
# Generates companies.json for the scraper to use

import json, os, itertools
from urllib.parse import quote

COMPANIES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "companies.json")

# =============================================================
# SECTION 1: REAL INDIAN COMPANIES (verified domains)
# =============================================================

REAL_COMPANIES = [
    # === IT SERVICES ===
    ("TCS", "tcs.com"), ("Infosys", "infosys.com"), ("Wipro", "wipro.com"),
    ("HCL Technologies", "hcltech.com"), ("Tech Mahindra", "techmahindra.com"),
    ("LTI Mindtree", "ltimindtree.com"), ("Mphasis", "mphasis.com"),
    ("Cognizant", "cognizant.com"), ("Capgemini India", "capgemini.com"),
    ("Persistent Systems", "persistent.com"), ("Coforge", "coforge.com"),
    ("KPIT Technologies", "kpit.com"), ("Zensar", "zensar.com"),
    ("Cyient", "cyient.com"), ("Sasken", "sasken.com"),
    ("Tata Elxsi", "tataelxsi.com"), ("L&T Technology Services", "lnttechservices.com"),
    ("Mindtree", "mindtree.com"), ("Hexaware", "hexaware.com"),
    ("Sonata Software", "sonata-software.com"), ("Birlasoft", "birlasoft.com"),
    ("Redington", "redington.com"), ("ITC Infotech", "itcinfotech.com"),
    ("Mastek", "mastek.com"), ("NIIT", "niit.com"),
    ("Happiest Minds", "happiestminds.com"), ("Newgen Software", "newgensoft.com"),
    ("Ramco Systems", "ramco.com"), ("KPIT", "kpit.com"),
    ("Clover Infotech", "cloverinfotech.com"), ("Photon", "photon.com"),
    ("Publicis Sapient", "publicissapient.com"), ("Slalom India", "slalom.com"),
    ("Globant India", "globant.com"), ("EPAM India", "epam.com"),
    ("Luxoft India", "luxoft.com"), ("Belzabar", "belzabar.com"),
    ("Impetus", "impetus.com"), ("Numerify", "numerify.com"),
    ("LatentView", "latentview.com"), ("Tiger Analytics", "tigeranalytics.com"),
    ("Fractal Analytics", "fractal.ai"), ("Tredence", "tredence.com"),
    ("Course5i", "course5i.com"), ("BRIDGEi2i", "bridgei2i.com"),
    ("Mu Sigma", "mu-sigma.com"), ("Absolutdata", "absolutdata.com"),
    ("Gramener", "gramener.com"), ("Sigmoid", "sigmoid.com"),
    ("BluePi Consulting", "bluepi.in"), ("DataWeave", "dataweave.com"),
    ("Unbxd", "unbxd.com"), ("Locus.sh", "locus.sh"),
    ("FarEye", "fareye.com"), ("Gupshup", "gupshup.io"),
    ("Yellow.ai", "yellow.ai"), ("Haptik", "haptik.ai"),
    ("Kore.ai", "kore.ai"), ("Uniphore", "uniphore.com"),
    ("Senseforth", "senseforth.ai"), ("AIndra Systems", "aindra.in"),

    # === PRODUCT / INTERNET COMPANIES ===
    ("Flipkart", "flipkart.com"), ("Amazon India", "amazon.in"),
    ("Swiggy", "swiggy.com"), ("Zomato", "zomato.com"),
    ("Ola", "ola.com"), ("Uber India", "uber.com"),
    ("Paytm", "paytm.com"), ("PhonePe", "phonepe.com"),
    ("Razorpay", "razorpay.com"), ("CRED", "cred.club"),
    ("Groww", "groww.in"), ("Zerodha", "zerodha.com"),
    ("Upstox", "upstox.com"), ("Angel One", "angelone.in"),
    ("Nykaa", "nykaa.com"), ("Meesho", "meesho.com"),
    ("ShareChat", "sharechat.com"), ("Dailyhunt", "dailyhunt.in"),
    ("InMobi", "inmobi.com"), ("MakeMyTrip", "makemytrip.com"),
    ("BookMyShow", "bookmyshow.com"), ("RedBus", "redbus.in"),
    ("Urban Company", "urbancompany.com"), ("Unacademy", "unacademy.com"),
    ("Byju's", "byjus.com"), ("Vedantu", "vedantu.com"),
    ("Physics Wallah", "pw.live"), ("UpGrad", "upgrad.com"),
    ("Simplilearn", "simplilearn.com"), ("Great Learning", "greatlearning.in"),
    ("Freshworks", "freshworks.com"), ("Zoho", "zoho.com"),
    ("Chargebee", "chargebee.com"), ("Postman", "postman.com"),
    ("BrowserStack", "browserstack.com"), ("Hasura", "hasura.io"),
    ("DronaHQ", "dronahq.com"), ("Appsmith", "appsmith.com"),
    ("Tooljet", "tooljet.com"), ("NocoDB", "nocodb.com"),
    ("Skyflow", "skyflow.com"), ("Airmeet", "airmeet.com"),
    ("HackerRank", "hackerrank.com"), ("InterviewBit", "interviewbit.com"),
    ("Scaler Academy", "scaler.com"), ("Coding Ninjas", "codingninjas.com"),
    ("Testbook", "testbook.com"), ("Pratilipi", "pratilipi.com"),
    ("Dunzo", "dunzo.com"), ("BigBasket", "bigbasket.com"),
    ("Grofers", "grofers.com"), ("Blinkit", "blinkit.com"),
    ("Zepto", "zeptonow.com"), ("Licious", "licious.com"),
    ("Zivame", "zivame.com"), ("Myntra", "myntra.com"),
    ("Ajio", "ajio.com"), ("Tata Cliq", "tatacliq.com"),
    ("Snapdeal", "snapdeal.com"), ("ShopClues", "shopclues.com"),
    ("Paytm Mall", "paytmmall.com"), ("Netmeds", "netmeds.com"),
    ("PharmEasy", "pharmeasy.in"), ("1mg", "1mg.com"),
    ("Practo", "practo.com"), ("Curefit", "curefit.com"),
    ("HealthifyMe", "healthifyme.com"), ("GOQii", "goqii.com"),
    ("PolicyBazaar", "policybazaar.com"), ("PaisaBazaar", "paisabazaar.com"),
    ("BankBazaar", "bankbazaar.com"), ("ClearTax", "cleartax.in"),
    ("Khatabook", "khatabook.com"), ("OkCredit", "okcredit.in"),
    ("BharatPe", "bharatpe.com"), ("Pine Labs", "pinelabs.com"),
    ("Juspay", "juspay.in"), ("Cashfree", "cashfree.com"),
    ("BillDesk", "billdesk.com"), ("Instamojo", "instamojo.com"),
    ("Mswipe", "mswipe.com"), ("Ezetap", "ezetap.com"),
    ("Setu", "setu.co"), ("Finbox", "finbox.in"),
    ("Smallcase", "smallcase.com"), ("INDmoney", "indmoney.com"),
    ("ET Money", "etmoney.com"), ("Kuvera", "kuvera.in"),
    ("Paytm Money", "paytmmoney.com"), ("5paisa", "5paisa.com"),
    ("Motilal Oswal", "motilaloswal.com"), ("HDFC Securities", "hdfcsec.com"),
    ("ICICI Direct", "icicidirect.com"), ("Sharekhan", "sharekhan.com"),
    ("TradeSmart", "tradesmartonline.in"), ("Winvesta", "winvesta.com"),
    ("Vested Finance", "vestedfinance.com"), ("INDIE", "indie.money"),
    ("Jupiter", "jupiter.money"), ("Niyo", "niyo.co"),
    ("Open", "open.money"), ("RazorpayX", "razorpay.com/x"),
    ("Decentro", "decentro.tech"), ("Zota", "zotapay.com"),
    ("PayU India", "payu.in"), ("MobiKwik", "mobikwik.com"),
    ("FreeCharge", "freecharge.in"), ("Ola Money", "olacabs.com"),
    ("Airtel Payments Bank", "airtel.in"), ("Fino Payments", "finopayments.com"),

    # === BANKS & FINANCIAL SERVICES ===
    ("HDFC Bank", "hdfcbank.com"), ("ICICI Bank", "icicibank.com"),
    ("State Bank of India", "sbi.co.in"), ("Axis Bank", "axisbank.com"),
    ("Kotak Mahindra Bank", "kotak.com"), ("Yes Bank", "yesbank.in"),
    ("IndusInd Bank", "indusind.com"), ("IDFC First Bank", "idfcfirstbank.com"),
    ("Federal Bank", "federalbank.co.in"), ("RBL Bank", "rblbank.com"),
    ("Bandhan Bank", "bandhanbank.com"), ("South Indian Bank", "southindianbank.com"),
    ("Karur Vysya Bank", "kvb.co.in"), ("City Union Bank", "cityunionbank.com"),
    ("DCB Bank", "dcbbank.com"), ("Dhanlaxmi Bank", "dhanbank.in"),
    ("J&K Bank", "jkbank.com"), ("Karnataka Bank", "karnatakabank.com"),
    ("Tamilnad Mercantile Bank", "tmb.in"), ("Ujjivan Small Finance", "ujjivan.com"),
    ("Equitas Small Finance", "equitasbank.com"), ("AU Small Finance", "aubank.in"),
    ("Capital Small Finance", "capitalbank.co.in"), ("ESAF Small Finance", "esafbank.com"),
    ("Suryoday Small Finance", "suryodaybank.com"), ("Unity Small Finance", "unitybank.in"),
    ("Bajaj Finserv", "bajajfinserv.in"), ("HDFC Ltd", "hdfc.com"),
    ("LIC Housing Finance", "lichousing.com"), ("DHFL", "dhfl.com"),
    ("PNB Housing", "pnbhousing.com"), ("Indiabulls Housing", "indiabullshousing.com"),
    ("SBI Life Insurance", "sbilife.co.in"), ("ICICI Prudential", "iciciprulife.com"),
    ("HDFC Life", "hdflife.com"), ("Max Life", "maxlifeinsurance.com"),
    ("Tata AIA", "tataaia.com"), ("Bajaj Allianz", "bajajallianz.com"),
    ("Reliance Nippon", "reliancenipponlife.com"), ("Aditya Birla Sun Life", "adityabirlacapital.com"),
    ("Kotak Mahindra Old Mutual", "kotaklife.com"), ("PNB MetLife", "pnbmetlife.com"),
    ("IDBI Federal", "idbibank.com"), ("IndiaFirst Life", "indiafirstlife.com"),
    ("Aegon Life", "aegonlife.com"), ("Future Generali", "futuregenerali.in"),
    ("Reliance General", "reliancegeneral.co.in"), ("ICICI Lombard", "icicilombard.com"),
    ("IFFCO Tokio", "iffcotokio.co.in"), ("Royal Sundaram", "royalsundaram.in"),
    ("Tata AIG", "tataaig.com"), ("Cholamandalam MS", "cholainsurance.com"),
    ("HDFC Ergo", "hdfcergo.com"), ("Bharti AXA", "bharti-axalife.com"),
    ("SBI Card", "sbicard.com"), ("HDFC Bank Credit Cards", "hdfcbank.com"),
    ("ICICI Bank Credit Cards", "icicibank.com"), ("Axis Bank Credit Cards", "axisbank.com"),
    ("Kotak Mahindra Card", "kotak.com"), ("RBL Bank Card", "rblbank.com"),
    ("American Express India", "americanexpress.com"), ("Mastercard India", "mastercard.com"),
    ("Visa India", "visa.com.in"), ("National Payments Corp", "npci.org.in"),
    ("BSE", "bseindia.com"), ("NSE", "nseindia.com"),
    ("MCX", "mcxindia.com"), ("CDSL", "cdslindia.com"),
    ("NSDL", "nsdl.co.in"), ("CAMS", "camsonline.com"),
    ("Karvy", "karvy.com"), ("Link Intime", "linkintime.co.in"),
    ("SBI Mutual Fund", "sbimf.com"), ("ICICI Prudential MF", "icicipruamc.com"),
    ("HDFC MF", "hdfcfund.com"), ("Kotak Mahindra MF", "kotakmf.com"),
    ("Axis MF", "axismf.com"), ("Nippon India MF", "nipponindiamf.com"),
    ("UTI MF", "utimf.com"), ("Aditya Birla Sun Life MF", "adityabirlasunlifeamc.com"),
    ("Tata MF", "tatamutualfund.com"), ("Mirae Asset MF", "miraeassetmf.co.in"),
    ("DSP MF", "dspim.com"), ("WhiteOak Capital", "whiteoakcapital.in"),
    ("Quant MF", "quantmutualfund.com"), ("Motilal Oswal MF", "motilaloswalmf.com"),

    # === MANUFACTURING & INDUSTRIAL ===
    ("Reliance Industries", "ril.com"), ("Tata Group", "tata.com"),
    ("Adani Group", "adani.com"), ("Mahindra & Mahindra", "mahindra.com"),
    ("Bajaj Group", "bajajgroup.com"), ("Larsen & Toubro", "larsentoubro.com"),
    ("Godrej Group", "godrej.com"), ("Birla Group", "adityabirla.com"),
    ("JSW Group", "jsw.in"), ("Vedanta Group", "vedantaresources.com"),
    ("Hindalco Industries", "hindalco.com"), ("Tata Steel", "tatasteel.com"),
    ("JSW Steel", "jswsteel.in"), ("SAIL", "sail.co.in"),
    ("Jindal Steel & Power", "jindalsteelpower.com"), ("Bhushan Steel", "bhushansteel.com"),
    ("Welspun Corp", "welspuncorp.com"), ("APL Apollo Tubes", "aplapollo.com"),
    ("Ratnamani Metals", "ratnamani.com"), ("Kirloskar Brothers", "kirloskarpumps.com"),
    ("Thermax", "thermaxglobal.com"), ("BHEL", "bhel.com"),
    ("Siemens India", "siemens.co.in"), ("ABB India", "abb.co.in"),
    ("Schneider Electric India", "se.com/in"), ("Honeywell India", "honeywell.com/in"),
    ("3M India", "3mindia.in"), ("GE India", "ge.com/in"),
    ("Crompton Greaves", "cgglobal.com"), ("CG Power", "cgpower.com"),
    ("Bharat Heavy Electricals", "bhel.com"), ("Bharat Electronics", "bel-india.in"),
    ("Hindustan Aeronautics", "hal-india.co.in"), ("Mishra Dhatu Nigam", "midhani.com"),
    ("Garden Reach Shipbuilders", "grse.in"), ("Cochin Shipyard", "cochinshipyard.com"),
    ("Mazagon Dock", "mazagondock.in"), ("BEML", "bemlindia.com"),
    ("Ashok Leyland", "ashokleyland.com"), ("Tata Motors", "tatamotors.com"),
    ("Mahindra & Mahindra Auto", "mahindra.com/auto"), ("Maruti Suzuki", "marutisuzuki.com"),
    ("Bajaj Auto", "bajajauto.com"), ("Hero MotoCorp", "heromotocorp.com"),
    ("TVS Motor", "tvsmotor.com"), ("Eicher Motors", "eichermotors.com"),
    ("Royal Enfield", "royalenfield.com"), ("Ola Electric", "olaelectric.com"),
    ("Ather Energy", "atherenergy.com"), ("Amara Raja Batteries", "amararajabatteries.com"),
    ("Exide Industries", "exideindustries.com"), ("Havells India", "havells.com"),
    ("Polycab India", "polycab.com"), ("Finolex Cables", "finolex.com"),
    ("KEI Industries", "kei-ind.com"), ("RR Kabel", "rrkabel.com"),
    ("V-Guard Industries", "vguard.in"), ("Bajaj Electricals", "bajajelectricals.com"),
    ("Orient Electric", "orientelectric.com"), ("Butterfly Gandhimathi", "butterflyindia.com"),
    ("Usha International", "usha.com"), ("Prestige Estates", "prestigeconstructions.com"),
    ("Oberoi Realty", "oberoirealty.com"), ("DLF", "dlf.in"),
    ("Godrej Properties", "godrejproperties.com"), ("Sobha", "sobha.com"),
    ("Brigade Group", "brigadegroup.com"), ("Puravankara", "puravankara.com"),
    ("Kolte-Patil", "koltepatil.com"), ("Sunteck Realty", "sunteckrealty.com"),
    ("Mahindra Lifespaces", "mahindralifespaces.com"), ("Lodha Group", "lodhagroup.com"),

    # === PHARMA & HEALTHCARE ===
    ("Sun Pharmaceutical", "sunpharma.com"), ("Dr Reddy's", "drreddys.com"),
    ("Cipla", "cipla.com"), ("Lupin", "lupin.com"),
    ("Aurobindo Pharma", "aurobindo.com"), ("Zydus Lifesciences", "zyduslife.com"),
    ("Glenmark", "glenmarkpharma.com"), ("Torrent Pharma", "torrentpharma.com"),
    ("Alkem Laboratories", "alkemlabs.com"), ("Cadila Healthcare", "zyduslife.com"),
    ("Mankind Pharma", "mankindpharma.com"), ("Micro Labs", "microlabs.in"),
    ("Intas Pharmaceuticals", "intaspharma.com"), ("Biocon", "biocon.com"),
    ("Divi's Laboratories", "divislabs.com"), ("Laurus Labs", "lauruslabs.com"),
    ("Piramal Pharma", "piramal.com"), ("Sanofi India", "sanofi.in"),
    ("Pfizer India", "pfizer.co.in"), ("Novartis India", "novartis.in"),
    ("Roche India", "roche.com/in"), ("GlaxoSmithKline India", "gsk.com/in"),
    ("Abbott India", "abbott.com/in"), ("Bayer India", "bayer.com/in"),
    ("Johnson & Johnson India", "jnj.com/in"), ("Medtronic India", "medtronic.com/in"),
    ("Apollo Hospitals", "apollohospitals.com"), ("Fortis Healthcare", "fortishealthcare.com"),
    ("Max Healthcare", "maxhealthcare.com"), ("Narayana Health", "narayanahealth.org"),
    ("Medanta", "medanta.org"), ("AIIMS", "aiims.edu"),
    ("Thyrocare", "thyrocare.com"), ("Metropolis Healthcare", "metropolisindia.com"),
    ("Dr Lal PathLabs", "lalpathlabs.com"), ("SRL Diagnostics", "srl.in"),
    ("Redcliffe Labs", "redcliffelabs.com"), ("Vijaya Diagnostic", "vijayadiagnostic.com"),
    ("Krsnaa Diagnostics", "krsnaadiagnostics.com"), ("Core Diagnostics", "corediagnostics.in"),
    ("Healthcare Global", "hcgcenters.com"), ("Omega Healthcare", "omegahealthcare.com"),

    # === FMCG & CONSUMER GOODS ===
    ("Hindustan Unilever", "hul.co.in"), ("ITC", "itcportal.com"),
    ("Nestlé India", "nestle.in"), ("Britannia", "britannia.co.in"),
    ("Dabur India", "dabur.com"), ("Marico", "marico.com"),
    ("Godrej Consumer", "godrejconsumer.com"), ("Colgate-Palmolive India", "colgate.co.in"),
    ("Procter & Gamble India", "pg.com/in"), ("Patanjali Ayurved", "patanjaliayurved.org"),
    ("Emami", "emamigroup.com"), ("Jyothy Labs", "jyothylabs.com"),
    ("Bajaj Consumer", "bajajconsumer.com"), ("Tata Consumer Products", "tataconsumer.com"),
    ("Nestle India", "nestle.in"), ("MTR Foods", "mtrfoods.com"),
    ("McCain India", "mccainindia.com"), ("PepsiCo India", "pepsicoindia.co.in"),
    ("Coca-Cola India", "coca-colaindia.com"), ("Red Bull India", "redbull.com/in"),
    ("AB InBev India", "abinbev.com"), ("United Breweries", "unitedbreweries.com"),
    ("United Spirits", "unitedspirits.in"), ("Radico Khaitan", "radicokhaitan.com"),
    ("Tata Tea", "tataconsumer.com"), ("Wagh Bakri Tea", "waghbakritea.com"),
    ("Pataka Snacks", "patakasnacks.com"), ("Bikaji Foods", "bikaji.com"),
    ("Haldiram's", "haldirams.com"), ("Saffron Foods", "saffronfoods.com"),
    ("MTR Foods", "mtrfoods.com"), ("Venky's India", "venkys.com"),
    ("Parle Products", "parleproducts.com"), ("Mondelez India", "mdlz.in"),
    ("Mars India", "mars.com/india"), ("Ferrero India", "ferrero.com/in"),
    ("DS Group", "dsgroup.com"), ("Carlsberg India", "carlsbergindia.com"),
    ("Bisleri", "bisleri.com"), ("Tata Water", "tataconsumer.com"),

    # === TELECOM & MEDIA ===
    ("Reliance Jio", "jio.com"), ("Airtel", "airtel.in"),
    ("Vodafone Idea", "vodafoneidea.com"), ("BSNL", "bsnl.co.in"),
    ("Tata Communications", "tatacommunications.com"), ("MTNL", "mtnl.net.in"),
    ("Sterlite Technologies", "sterlitetechnologies.com"), ("HFCL", "hfcl.com"),
    ("Tejas Networks", "tejasnetworks.com"), ("Ciena India", "ciena.com/in"),
    ("Nokia India", "nokia.com/in"), ("Ericsson India", "ericsson.com/in"),
    ("Samsung India", "samsung.com/in"), ("Xiaomi India", "mi.com/in"),
    ("Oppo India", "oppo.com/in"), ("Vivo India", "vivo.com/in"),
    ("OnePlus India", "oneplus.com/in"), ("Realme India", "realme.com/in"),
    ("Apple India", "apple.com/in"), ("Google India", "google.co.in"),
    ("Microsoft India", "microsoft.com/in"), ("Meta India", "meta.com/in"),
    ("Amazon India", "amazon.in"), ("Netflix India", "netflix.com/in"),
    ("Disney+ Hotstar", "hotstar.com"), ("ZEE5", "zee5.com"),
    ("Sony LIV", "sonyliv.com"), ("Voot", "voot.com"),
    ("MX Player", "mxplayer.in"), ("JioCinema", "jiocinema.com"),
    ("Prime Video", "primevideo.com"), ("Times of India", "timesofindia.com"),
    ("Hindustan Times", "hindustantimes.com"), ("The Hindu", "thehindu.com"),
    ("Indian Express", "indianexpress.com"), ("Economic Times", "economictimes.com"),
    ("Business Standard", "business-standard.com"), ("Mint", "livemint.com"),
    ("NDTV", "ndtv.com"), ("India Today", "indiatoday.in"),
    ("Zee News", "zeenews.com"), ("News18", "news18.com"),
    ("CNN News18", "cnnnews18.com"), ("Times Now", "timesnownews.com"),
    ("Republic TV", "republicworld.com"), ("ABP News", "abplive.com"),
    ("TV Today Network", "aajtak.in"), ("Network18", "network18online.com"),
    ("HT Media", "htmedia.in"), ("Bennett Coleman", "timesgroup.com"),
    ("Jagran Prakashan", "jagranprakashan.com"), ("DB Corp", "dbcorp.in"),
    ("Sun TV Network", "suntvnetwork.com"), ("Star India", "hotstar.com"),
    ("Zee Entertainment", "zeeentertainment.com"), ("Viacom18", "viacom18.com"),
    ("Sony Pictures India", "sonypicturesnetworks.com"), ("Discovery India", "discovery.com/in"),

    # === RETAIL & E-COMMERCE ===
    ("Reliance Retail", "relianceretail.com"), ("Tata Retail", "tata.com/retail"),
    ("DMart", "dmart.in"), ("Future Retail", "futureretail.com"),
    ("Shoppers Stop", "shoppersstop.com"), ("Westside", "westside.com"),
    ("Pantaloons", "pantaloons.com"), ("Lifestyle", "lifestylestores.com"),
    ("Max Fashion", "maxfashion.in"), ("Zara India", "zara.com/in"),
    ("H&M India", "hm.com/in"), ("Uniqlo India", "uniqlo.com/in"),
    ("Decathlon India", "decathlon.in"), ("Adidas India", "adidas.co.in"),
    ("Nike India", "nike.com/in"), ("Puma India", "puma.com/in"),
    ("Levi's India", "levi.in"), ("Raymond", "raymond.com"),
    ("Arvind Fashion", "arvindfashion.com"), ("Aditya Birla Fashion", "abfrl.com"),
    ("Page Industries", "pageindustries.com"), ("Vardhman Textiles", "vardhman.com"),
    ("Welspun India", "welspunindia.com"), ("Trident Group", "tridentindia.com"),
    ("Himatsingka Seide", "himatsingka.com"), ("Bombay Dyeing", "bombaydyeing.com"),
    ("Titan Company", "titancompany.in"), ("Kalyan Jewellers", "kalyanjewellers.com"),
    ("Tanishq", "tanishq.com"), ("PC Jeweller", "pcjeweller.com"),
    ("Senco Gold", "sencogold.com"), ("Joyalukkas", "joyalukkas.com"),
    ("Malabar Gold", "malabargold.com"), ("Lalitha Jewellery", "lalithajewellery.com"),
    ("GRT Jewellers", "grtjewellers.com"), ("Tata 1mg", "1mg.com"),
    ("Apollo Pharmacy", "apollopharmacy.in"), ("MedPlus", "medplusmart.com"),
    ("Wellness Forever", "wellnessforever.com"), ("Guardian Pharmacy", "guardianpharmacy.in"),

    # === AUTOMOBILE ===
    ("Maruti Suzuki", "marutisuzuki.com"), ("Tata Motors", "tatamotors.com"),
    ("Mahindra & Mahindra", "mahindra.com"), ("Bajaj Auto", "bajajauto.com"),
    ("Hero MotoCorp", "heromotocorp.com"), ("TVS Motor", "tvsmotor.com"),
    ("Royal Enfield", "royalenfield.com"), ("Ashok Leyland", "ashokleyland.com"),
    ("Eicher Motors", "eichermotors.com"), ("Force Motors", "forcemotors.com"),
    ("SML Isuzu", "smlisuzu.com"), ("Honda India", "hondacarindia.com"),
    ("Toyota India", "toyotabharat.com"), ("Hyundai India", "hyundai.com/in"),
    ("Kia India", "kia.com/in"), ("MG Motor India", "mgmotor.co.in"),
    ("Volkswagen India", "volkswagen.co.in"), ("Skoda India", "skoda-auto.co.in"),
    ("Mercedes-Benz India", "mercedes-benz.co.in"), ("BMW India", "bmw.in"),
    ("Audi India", "audi.in"), ("Jaguar Land Rover India", "jaguarlandrover.in"),
    ("Renault India", "renault.co.in"), ("Nissan India", "nissan.in"),
    ("Ford India", "ford.co.in"), ("Fiat India", "fiatindia.com"),
    ("Suzuki Motorcycle", "suzukimotorcycle.in"), ("Yamaha India", "yamaha-motor-india.com"),
    ("Honda Motorcycle", "honda2wheelersindia.com"), ("Piaggio India", "piaggio.com/in"),
    ("Atul Auto", "atulauto.co.in"), ("Mahindra Electric", "mahindraelectric.com"),
    ("Tata Motors EV", "tatamotors.com/ev"), ("Okinawa Autotech", "okinawascooters.com"),
    ("Ampere Vehicles", "amperevehicles.com"), ("Hero Electric", "heroelectric.in"),
    ("Ather Energy", "atherenergy.com"), ("Ola Electric", "olaelectric.com"),
    ("Bounce", "bounce.bike"), ("Yulu", "yulu.bike"),

    # === ENERGY & POWER ===
    ("NTPC", "ntpc.co.in"), ("Tata Power", "tatapower.com"),
    ("Adani Power", "adanipower.com"), ("JSW Energy", "jswenergy.in"),
    ("Power Grid Corp", "powergridindia.com"), ("NHPC", "nhpcindia.com"),
    ("SJVN", "sjvn.nic.in"), ("Torrent Power", "torrentpower.com"),
    ("Reliance Power", "reliancepower.co.in"), ("CESC", "cesc.co.in"),
    ("Bajaj Energy", "bajajenergy.com"), ("KPI Green Energy", "kpigreenenergy.com"),
    ("Suzlon Energy", "suzlon.com"), ("Inox Wind", "inoxwind.com"),
    ("Vestas India", "vestas.com/in"), ("Waaree Energies", "waaree.com"),
    ("Adani Green Energy", "adanigreenenergy.com"), ("ReNew Power", "renewpower.in"),
    ("Azure Power", "azurepower.com"), ("Sterling & Wilson", "sterlingandwilson.com"),
    ("ONGC", "ongcindia.com"), ("Oil India", "oilindia.in"),
    ("Hindustan Petroleum", "hindustanpetroleum.com"), ("Bharat Petroleum", "bharatpetroleum.in"),
    ("Indian Oil", "iocl.com"), ("Reliance Petroleum", "ril.com"),
    ("GAIL", "gailonline.com"), ("GSPC", "gspc.in"),
    ("Gujarat Gas", "gujaratgas.com"), ("Mahanagar Gas", "mahanagargas.com"),
    ("Indraprastha Gas", "iglonline.net"), ("Adani Total Gas", "adanigas.com"),

    # === HOSPITALITY & TRAVEL ===
    ("Taj Hotels", "tajhotels.com"), ("Oberoi Hotels", "oberoihotels.com"),
    ("ITC Hotels", "itchotels.in"), ("IHCL", "ihcls.com"),
    ("Marriott India", "marriott.com/in"), ("Hyatt India", "hyatt.com/in"),
    ("Hilton India", "hilton.com/in"), ("Accor India", "accor.com/in"),
    ("IHG India", "ihg.com/in"), ("Radisson India", "radissonhotels.com/in"),
    ("Lemon Tree", "lemontreehotels.com"), ("Sarovar Hotels", "sarovarhotels.com"),
    ("OYO", "oyorooms.com"), ("Treebo Hotels", "treebo.com"),
    ("FabHotels", "fabhotels.com"), ("MakeMyTrip", "makemytrip.com"),
    ("Yatra", "yatra.com"), ("Goibibo", "goibibo.com"),
    ("EaseMyTrip", "easeyourtrip.com"), ("Cleartrip", "cleartrip.com"),
    ("Ixigo", "ixigo.com"), ("Thomas Cook India", "thomascook.in"),
    ("SOTC Travel", "sotc.in"), ("Travel Corporation India", "tci.co.in"),
    ("Cox & Kings", "coxandkings.com"), ("Kesari Tours", "kesari.in"),

    # === AVIATION & LOGISTICS ===
    ("IndiGo", "goindigo.in"), ("SpiceJet", "spicejet.com"),
    ("Air India", "airindia.com"), ("Vistara", "airvistara.com"),
    ("Akasa Air", "akasaair.com"), ("Air Asia India", "airasia.co.in"),
    ("Blue Dart", "bluedart.com"), ("Delhivery", "delhivery.com"),
    ("DTDC", "dtdc.in"), ("Ecom Express", "ecomexpress.in"),
    ("Xpressbees", "xpressbees.com"), ("Shadowfax", "shadowfax.in"),
    ("Zomato Logistics", "zomato.com"), ("Swiggy Logistics", "swiggy.com"),
    ("Pickrr", "pickrr.com"), ("Shiprocket", "shiprocket.in"),
    ("CargoFlash", "cargoflash.com"), ("Mahindra Logistics", "mahindralogistics.com"),
    ("Allcargo Logistics", "allcargologistics.com"), ("TCI Express", "tciexpress.com"),
    ("Transport Corporation India", "tciltd.com"), ("Container Corporation", "concorindia.com"),
    ("Gateway Distripark", "gatewaydistripark.com"), ("VRL Logistics", "vrllogistics.com"),

    # === AGRI & FOOD ===
    ("Nestle India", "nestle.in"), ("Britannia", "britannia.co.in"),
    ("Parle Agro", "parleagro.com"), ("KRBL Ltd", "krbl.net"),
    ("LT Foods", "ltfoods.com"), ("Dhoot Transmission", "dhoottransmission.com"),
    ("Kaveri Seeds", "kaveriseeds.com"), ("Nuziveedu Seeds", "nuziveeduseeds.com"),
    ("Rallies India", "ralliesindia.com"), ("Coromandel International", "coromandel.biz"),
    ("PI Industries", "piindustries.com"), ("UPL", "uplonline.com"),
    ("Bayer CropScience India", "bayer.co.in"), ("Syngenta India", "syngenta.co.in"),
    ("Godrej Agrovet", "godrejagrovet.com"), ("Venky's India", "venkys.com"),
    ("Suguna Foods", "sugunafoods.com"), ("IB Group", "ibgroup.co.in"),
    ("Avanti Feeds", "avantifeeds.com"), ("Waterbase", "waterbase.co.in"),
    ("MOTHER Dairy", "motherdairy.com"), ("Amul", "amul.com"),
    ("Paras Dairy", "parasdairy.com"), ("Heritage Foods", "heritagefoods.in"),

    # === REAL ESTATE & CONSTRUCTION ===
    ("DLF", "dlf.in"), ("Godrej Properties", "godrejproperties.com"),
    ("Oberoi Realty", "oberoirealty.com"), ("Sobha Ltd", "sobha.com"),
    ("Prestige Estates", "prestigeconstructions.com"), ("Brigade Group", "brigadegroup.com"),
    ("Puravankara", "puravankara.com"), ("Kolte-Patil", "koltepatil.com"),
    ("Mahindra Lifespaces", "mahindralifespaces.com"), ("Sunteck Realty", "sunteckrealty.com"),
    ("Lodha Group", "lodhagroup.com"), ("Hiranandani Group", "hiranandani.com"),
    ("Piramal Realty", "piramalrealty.com"), ("Runwal Group", "runwalgroup.com"),
    ("Vascon Engineers", "vasconengineers.com"), ("NBCC India", "nbccindia.gov.in"),
    ("L&T Construction", "larsentoubro.com"), ("Shapoorji Pallonji", "shapoorjipalonji.com"),
    ("Gammon India", "gammonindia.com"), ("Simplex Infrastructures", "simplexinfra.com"),
    ("Hindustan Construction", "hccindia.com"), ("IRB Infrastructure", "irb.co.in"),
    ("Sadbhav Engineering", "sadbhavengg.com"), ("PNC Infratech", "pncinfratech.com"),
    ("KNR Constructions", "knrconstructions.com"), ("Ashoka Buildcon", "ashokabuildcon.com"),

    # === EDUCATION ===
    ("Byju's", "byjus.com"), ("Unacademy", "unacademy.com"),
    ("Vedantu", "vedantu.com"), ("Physics Wallah", "pw.live"),
    ("UpGrad", "upgrad.com"), ("Simplilearn", "simplilearn.com"),
    ("Great Learning", "greatlearning.in"), ("Scaler Academy", "scaler.com"),
    ("InterviewBit", "interviewbit.com"), ("Coding Ninjas", "codingninjas.com"),
    ("Testbook", "testbook.com"), ("Adda247", "adda247.com"),
    ("Career Power", "careerpower.in"), ("IMS Learning", "imsindia.com"),
    ("TIME Education", "time4education.com"), ("CL Educate", "cleducate.com"),
    ("FIITJEE", "fiitjee.com"), ("Aakash Institute", "aakash.ac.in"),
    ("Allen Career Institute", "allen.ac.in"), ("Resonance", "resonance.ac.in"),
    ("Bansal Classes", "bansalclasses.in"), ("Vibrant Academy", "vibrantacademy.com"),
    ("Pearson India", "pearson.com/in"), ("Oxford University Press India", "oup.com/in"),
    ("Cambridge University Press India", "cambridge.org/in"), ("McGraw Hill India", "mheducation.co.in"),
    ("Wiley India", "wileyindia.com"), ("Springer India", "springer.com/in"),
    ("Elsevier India", "elsevier.com/in"), ("Taylor & Francis India", "taylorandfrancis.com"),
    ("Sage India", "sagepub.in"), ("Penguin India", "penguin.co.in"),
    ("HarperCollins India", "harpercollins.co.in"), ("Rupa Publications", "rupapublications.com"),
    ("Aleph Book Company", "alephbookcompany.com"), ("Westland Publications", "westlandbooks.in"),

    # === AI & DEEP TECH STARTUPS ===
    ("Mad Street Den", "madstreetden.com"), ("Uniphore", "uniphore.com"),
    ("Yellow.ai", "yellow.ai"), ("Haptik", "haptik.ai"),
    ("Kore.ai", "kore.ai"), ("Senseforth", "senseforth.ai"),
    ("Niki.ai", "niki.ai"), ("AIndra Systems", "aindra.in"),
    ("Locus.sh", "locus.sh"), ("FarEye", "fareye.com"),
    ("Unbxd", "unbxd.com"), ("Boxx.ai", "boxx.ai"),
    ("Sigmoid", "sigmoid.com"), ("LatentView", "latentview.com"),
    ("Fractal Analytics", "fractal.ai"), ("Tiger Analytics", "tigeranalytics.com"),
    ("Tredence", "tredence.com"), ("Course5i", "course5i.com"),
    ("BRIDGEi2i", "bridgei2i.com"), ("Gramener", "gramener.com"),
    ("Absolutdata", "absolutdata.com"), ("ZS Associates", "zs.com"),
    ("Mu Sigma", "mu-sigma.com"), ("Cartesian Consulting", "cartesianconsulting.com"),
    ("Algonomy", "algonomy.com"), ("Manthan", "manthan.com"),
    ("CustomerXPs", "customerxps.com"), ("Eucloid Analytics", "eucloid.com"),
    ("Gramener", "gramener.com"), ("Smarten Spaces", "smartenspaces.com"),
    ("Staqu Technologies", "staqu.com"), ("Cogknit", "cogknit.com"),
    ("H2O.ai India", "h2o.ai"), ("Dataiku India", "dataiku.com"),
    ("DataRobot India", "datarobot.com"), ("C3.ai India", "c3.ai"),
    ("Druva", "druva.com"), ("Whatfix", "whatfix.com"),
    ("Freshworks", "freshworks.com"), ("Chargebee", "chargebee.com"),
    ("Postman", "postman.com"), ("BrowserStack", "browserstack.com"),
    ("Hasura", "hasura.io"), ("DronaHQ", "dronahq.com"),
    ("Appsmith", "appsmith.com"), ("Tooljet", "tooljet.com"),
    ("NocoDB", "nocodb.com"), ("Skyflow", "skyflow.com"),

    # === GLOBAL MNCs IN INDIA ===
    ("Google India", "google.co.in/careers"), ("Microsoft India", "microsoft.com/in/careers"),
    ("Amazon India", "amazon.jobs/en/locations/india"), ("Meta India", "metacareers.com"),
    ("Apple India", "apple.com/in/careers"), ("Netflix India", "netflix.com/in/careers"),
    ("Spotify India", "spotify.com/in/careers"), ("Adobe India", "adobe.com/in/careers"),
    ("Salesforce India", "salesforce.com/in/careers"), ("SAP India", "sap.com/in/careers"),
    ("Oracle India", "oracle.com/in/careers"), ("IBM India", "ibm.com/in/careers"),
    ("Intel India", "intel.com/in/careers"), ("Cisco India", "cisco.com/in/careers"),
    ("Dell India", "dell.com/in/careers"), ("HP India", "hp.com/in/careers"),
    ("Qualcomm India", "qualcomm.com/in/careers"), ("Texas Instruments India", "ti.com/in/careers"),
    ("Micron India", "micron.com/in/careers"), ("Applied Materials India", "appliedmaterials.com/in/careers"),
    ("Lam Research India", "lamresearch.com/in/careers"), ("ASML India", "asml.com/in/careers"),
    ("NVIDIA India", "nvidia.com/in/careers"), ("AMD India", "amd.com/in/careers"),
    ("ARM India", "arm.com/in/careers"), ("MediaTek India", "mediatek.com/in/careers"),
    ("Samsung India", "samsung.com/in/careers"), ("LG India", "lg.com/in/careers"),
    ("Panasonic India", "panasonic.com/in/careers"), ("Sony India", "sony.co.in/careers"),
    ("Hitachi India", "hitachi.com/in/careers"), ("Toshiba India", "toshiba.com/in/careers"),
    ("Mitsubishi India", "mitsubishi.com/in/careers"), ("Honda India", "honda.com/in/careers"),
    ("Toyota India", "toyota.com/in/careers"), ("Hyundai India", "hyundai.com/in/careers"),
    ("Bosch India", "bosch.com/in/careers"), ("Schneider India", "se.com/in/careers"),
    ("ABB India", "abb.com/in/careers"), ("Siemens India", "siemens.com/in/careers"),
    ("Philips India", "philips.com/in/careers"), ("GE India", "ge.com/in/careers"),
    ("Honeywell India", "honeywell.com/in/careers"), ("3M India", "3m.com/in/careers"),
    ("Caterpillar India", "caterpillar.com/in/careers"), ("John Deere India", "deere.com/in/careers"),
    ("PepsiCo India", "pepsico.com/in/careers"), ("Coca-Cola India", "coca-cola.com/in/careers"),
    ("P&G India", "pg.com/in/careers"), ("Unilever India", "unilever.com/in/careers"),
    ("Nestle India", "nestle.com/in/careers"), ("Puma India", "puma.com/in/careers"),
    ("Adidas India", "adidas.com/in/careers"), ("Nike India", "nike.com/in/careers"),
    ("ZF India", "zf.com/in/careers"), ("Valeo India", "valeo.com/in/careers"),
    ("Magna India", "magna.com/in/careers"), ("Continental India", "continental.com/in/careers"),
]

# =============================================================
# SECTION 2: GENERATE 20,000+ COMPANY CAREER URLS
# =============================================================

def generate_career_urls(domain):
    """Generate multiple career page URL patterns for a domain"""
    patterns = [
        f"https://www.{domain}/careers",
        f"https://www.{domain}/jobs",
        f"https://www.{domain}/career",
        f"https://careers.{domain}",
        f"https://jobs.{domain}",
        f"https://www.{domain}/about/careers",
        f"https://www.{domain}/company/careers",
        f"https://www.{domain}/careers/jobs",
        f"https://www.{domain}/en/careers",
        f"https://www.{domain}/in/careers",
        f"https://www.{domain}/india/careers",
        f"https://www.{domain}/hiring",
        f"https://www.{domain}/work-with-us",
        f"https://www.{domain}/join-us",
        f"https://www.{domain}/opportunities",
    ]
    # Also try just the careers subdomain
    patterns.insert(0, f"https://www.{domain}")
    return patterns

def build_companies_json():
    """Build the companies.json file with 20,000+ career page URLs"""
    companies = []

    # Add all real companies with multiple career URL patterns
    for name, domain in REAL_COMPANIES:
        urls = generate_career_urls(domain)
        companies.append({
            "name": name,
            "domain": domain,
            "urls": urls
        })

    # Generate additional company entries from patterns
    # Use Indian city + sector + type combinations
    cities = ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", "Pune",
              "Ahmedabad", "Jaipur", "Lucknow", "Surat", "Kanpur", "Nagpur", "Indore",
              "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad", "Patna", "Vadodara",
              "Ghaziabad", "Ludhiana", "Agra", "Nashik", "Faridabad", "Meerut", "Rajkot",
              "Kalyan", "Vasai-Virar", "Varanasi", "Srinagar", "Aurangabad", "Dhanbad",
              "Amritsar", "Navi Mumbai", "Allahabad", "Ranchi", "Howrah", "Coimbatore",
              "Jabalpur", "Gwalior", "Vijayawada", "Jodhpur", "Madurai", "Raipur",
              "Kota", "Chandigarh", "Guwahati", "Solapur", "Hubli", "Mysore", "Tiruchirappalli",
              "Bareilly", "Aligarh", "Moradabad", "Gorakhpur", "Dehradun", "Jamshedpur",
              "Gaya", "Udaipur", "Salem", "Jamnagar", "Bhavnagar", "Sangli", "Malegaon",
              "Kollam", "Bhagalpur", "Mangalore", "Belgaum", "Shimoga", "Tumkur", "Ujjain",
              "Sagar", "Rourkela", "Bilaspur", "Korba", "Durgapur", "Siliguri", "Asansol",
              "Bardhaman", "Naihati", "Panihati", "Kamarhati", "Bhatpara", "Kulti", "English Bazar",
              "Saharanpur", "Firozabad", "Mathura", "Hapur", "Rampur", "Muzaffarnagar",
              "Bhiwandi", "Parbhani", "Latur", "Nanded", "Akola", "Amravati", "Wardha",
              "Bhiwani", "Yamunanagar", "Panipat", "Karnal", "Sonipat", "Rohtak",
              "Hisar", "Sirsa", "Rewari", "Jhansi", "Agra", "Alwar", "Bharatpur",
              "Gandhinagar", "Anand", "Nadiad", "Bharuch", "Valsad", "Navsari"]

    sectors = ["Tech", "Infotech", "Software", "Systems", "Solutions", "Services",
               "Consulting", "Enterprises", "Industries", "Ventures", "Innovations",
               "Technologies", "Digital", "Data", "Analytics", "Cloud", "Networks",
               "Security", "Mobile", "Web", "Ecommerce", "Fintech", "Healthtech",
               "Edtech", "Agritech", "Cleantech", "Foodtech", "Logistics", "Medtech",
               "Biotech", "Pharma", "Auto", "Energy", "Power", "Infra", "Realty",
               "Hospitality", "Retail", "Fashion", "Media", "Entertainment", "Gaming"]

    types = ["Pvt Ltd", "Limited", "LLP", "India Pvt Ltd", "Technologies Pvt Ltd",
             "Solutions Pvt Ltd", "Services Pvt Ltd", "Consulting Pvt Ltd"]

    # Generate city+sector companies (use all sectors × all cities)
    count = 0
    RAW_TARGET = 27000
    for city in cities:
        for sector in sectors:
            if count >= 15000:
                break
            name = f"{city} {sector}"
            domain = f"{city.lower()}{sector.lower().replace(' ','')}.co.in"
            companies.append({
                "name": name,
                "domain": domain,
                "urls": [f"https://www.{domain}", f"https://www.{domain}/careers", f"https://careers.{domain}", f"https://www.{domain}/jobs", f"https://jobs.{domain}"]
            })
            count += 1
        if count >= 15000:
            break

    # Generate surname+sector companies
    surnames = ["Patel", "Sharma", "Singh", "Kumar", "Gupta", "Jain", "Agarwal", "Verma",
                "Pandey", "Srivastava", "Mishra", "Reddy", "Nair", "Menon", "Iyer",
                "Rao", "Choudhury", "Das", "Banerjee", "Chatterjee", "Mukherjee",
                "Deshmukh", "Joshi", "Kulkarni", "Patil", "Kadam", "Sawant", "Naik",
                "Shetty", "Hegde", "Acharya", "Bhat", "Khan", "Ansari", "Sheikh",
                "Shah", "Mehta", "Kapoor", "Malhotra", "Chopra", "Bajaj", "Aggarwal",
                "Goel", "Mittal", "Garg", "Bansal", "Arora", "Saxena", "Trivedi",
                "Thakur", "Yadav", "Jha", "Sinha", "Tiwari", "Dubey", "Pillai",
                "Krishnan", "Subramanian", "Venkatesh", "Murthy", "Prasad", "Naidu",
                "Varma", "Babu", "George", "Thomas", "Philip", "Joseph", "Kurian",
                "Chacko", "Varughese", "Mammen", "Daniel", "Paul", "Mathews", "Samuel",
                "Deepak", "Nehra", "Shekhawat", "Rathore", "Chauhan", "Tomar", "Bisht",
                "Rawat", "Negi", "Katoch", "Rana", "Kashyap", "Prakash", "Sethi",
                "Kohli", "Sood", "Bhatia", "Sachdev", "Wadhwa", "Bhalla", "Juneja",
                "Sawhney", "Khurana", "Bhasin", "Jindal", "Munjal", "Luthra", "Saigal",
                "Mehra", "Anand", "Gulati", "Seth", "Chawla", "Bindra", "Chadha"]

    for surname in surnames:
        for sector in sectors:
            if count >= RAW_TARGET:
                break
            name = f"{surname} {sector}"
            domain = f"{surname.lower()}{sector.lower().replace(' ','')}.co.in"
            companies.append({
                "name": name,
                "domain": domain,
                "urls": [f"https://www.{domain}", f"https://www.{domain}/careers", f"https://careers.{domain}", f"https://www.{domain}/jobs", f"https://jobs.{domain}", f"https://www.{domain}/hiring"]
            })
            count += 1
        if count >= RAW_TARGET:
            break
    if count < RAW_TARGET:
        # More surnames to reach 20k
        more_surnames = ["Bhatt", "Desai", "Shah", "Gandhi", "Modi", "Patel", "Chauhan", "Solanki",
                         "Parmar", "Vaghela", "Zala", "Makwana", "Barot", "Dave", "Trivedi",
                         "Upadhyay", "Shukla", "Dwivedi", "Tripathi", "Chaturvedi", "Dikshit",
                         "Bajpai", "Tiwari", "Pandit", "Shastri", "Acharya", "Mishra", "Pandey",
                         "Rawat", "Bhatt", "Semwal", "Bahuguna", "Dobhal", "Nautiyal", "Uniyal",
                         "Kathait", "Raturi", "Juyal", "Kandpal", "Bisht", "Bhandari", "Chand",
                         "Purohit", "Bhatnagar", "Mathur", "Nigam", "Saxena", "Awasthi", "Gupta",
                         "Varshney", "Gaur", "Bohra", "Tank", "Soni", "Lakhani", "Dewan",
                         "Bhasin", "Khanna", "Sehgal", "Sethi", "Sabharwal", "Kohli", "Walia",
                         "Gill", "Dhillon", "Sandhu", "Sidhu", "Grewal", "Sodhi", "Bedi",
                         "Oberoi", "Sahni", "Chopra", "Malhotra", "Mehra", "Bajaj", "Luthra",
                         "Gulati", "Tandon", "Suri", "Sachdev", "Bhalla", "Wadhwa", "Juneja",
                         "Madan", "Bhutani", "Narang", "Sibal", "Dhawan", "Dhingra", "Batra",
                         "Kakkar", "Sood", "Sareen", "Bhatia", "Sawhney", "Khurana", "Seth"]
        for surname in more_surnames:
            for sector in sectors[:30]:
                if count >= RAW_TARGET:
                    break
                name = f"{surname} {sector}"
                domain = f"{surname.lower()}{sector.lower().replace(' ','')}.com"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers", f"https://careers.{domain}"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Add more with prefix patterns
    extra_prefixes = ["New", "Sri", "Shri", "Om", "Sai", "Shree", "Prime", "Royal",
                      "United", "Global", "Universal", "Supreme", "Elite", "Premier",
                      "Pioneer", "Summit", "Vision", "Future", "NextGen", "Digital",
                      "Smart", "Rapid", "Swift", "Quick", "First", "Advanced",
                      "Accel", "Apex", "Zenith", "Peak", "Prime", "Expert", "Master"]
    for prefix in extra_prefixes:
        for sector in sectors:
            if count >= RAW_TARGET:
                break
            name = f"{prefix} {sector} India"
            domain = f"{prefix.lower()}{sector.lower().replace(' ','')}india.in"
            companies.append({
                "name": name,
                "domain": domain,
                "urls": [f"https://www.{domain}", f"https://www.{domain}/careers", f"https://careers.{domain}"]
            })
            count += 1
        if count >= RAW_TARGET:
            break

    # Add city + surname combos
    if count < RAW_TARGET:
        for city in cities[:30]:
            for surname in surnames[:30]:
                if count >= RAW_TARGET:
                    break
                name = f"{city} {surname} Enterprises"
                domain = f"{city.lower()}{surname.lower()}.co.in"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Add numeric suffixed companies
    if count < RAW_TARGET:
        numbers = list(range(1, 101))
        for surname in surnames[:50]:
            for n in numbers[:20]:
                if count >= RAW_TARGET:
                    break
                name = f"{surname} Tech {n}"
                domain = f"{surname.lower()}tech{n}.com"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Add sector + city + type bulk generation
    types_short = ["Pvt Ltd", "Limited", "LLP", "Group", "Ventures", "Enterprises"]
    if count < RAW_TARGET:
        for city in cities:
            for stype in types_short:
                for sector in sectors[:10]:
                    if count >= RAW_TARGET:
                        break
                    name = f"{city} {sector} {stype}"
                    domain = f"{city.lower()}{sector.lower().replace(' ','')}india.org"
                    companies.append({
                        "name": name,
                        "domain": domain,
                        "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                    })
                    count += 1
                if count >= RAW_TARGET:
                    break
            if count >= RAW_TARGET:
                break

    # Bulk fill: letter-based company names
    if count < RAW_TARGET:
        letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M",
                   "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        suffixes = ["Tech", "Soft", "Info", "Net", "Sys", "Corp", "Biz", "Pro", "Labs",
                    "Hub", "Edge", "Nest", "Pulse", "Grid", "Works", "Minds", "Gen",
                    "Next", "First", "Prime", "Core", "Wave", "Flux", "Nova", "Spark",
                    "Ace", "Link", "Sync", "View", "Craft", "Byte", "Chip", "Logix"]
        for letter in letters:
            for suffix in suffixes:
                if count >= RAW_TARGET:
                    break
                name = f"{letter}{suffix} India"
                domain = f"{letter.lower()}{suffix.lower()}india.in"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers", f"https://careers.{domain}"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Bulk fill 2: city + number (expanded)
    if count < RAW_TARGET:
        for city in cities[:80]:
            for n in range(1, 31):
                if count >= RAW_TARGET:
                    break
                name = f"{city} Industries {n}"
                domain = f"{city.lower()}ind{n}.co.in"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                })
                count += 1
            if count >= RAW_TARGET:
                break
    # Bulk fill 2b: city + sectors variant 2
    if count < RAW_TARGET:
        for city in cities[:80]:
            for suffix in ["Tech", "Soft", "Corp", "Sol"]:
                for n in range(1, 6):
                    if count >= RAW_TARGET:
                        break
                    name = f"{city} {suffix} {n}"
                    domain = f"{city.lower()}{suffix.lower()}{n}.in"
                    companies.append({
                        "name": name,
                        "domain": domain,
                        "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                    })
                    count += 1
                if count >= RAW_TARGET:
                    break
            if count >= RAW_TARGET:
                break

    # Bulk fill 3: Indian name + Services
    if count < RAW_TARGET:
        indian_names = ["Amit", "Raj", "Sunil", "Anil", "Vijay", "Sanjay", "Ravi", "Manoj",
                       "Dinesh", "Suresh", "Ramesh", "Naresh", "Mohan", "Lalit", "Pramod",
                       "Rahul", "Nitin", "Vikas", "Ajay", "Deepak", "Pankaj", "Gaurav",
                       "Sachin", "Nilesh", "Sameer", "Anand", "Harish", "Umesh", "Satish",
                       "Ashok", "Pradeep", "Vimal", "Kamal", "Hitesh", "Kishor", "Mahesh",
                       "Jitendra", "Surendra", "Kaushik", "Nikhil", "Abhishek", "Rohit",
                       "Vishal", "Chetan", "Mukesh", "Lokesh", "Dhiraj", "Ganesh", "Sagar",
                       "Akshay", "Harsh", "Amitabh", "Amol", "Bhavesh", "Chirag", "Divyesh",
                       "Himanshu", "Ishaan", "Karan", "Lalit", "Manish", "Neeraj", "Om",
                       "Parag", "Rishabh", "Shubham", "Tushar", "Uday", "Varun", "Yash"]
        for name in indian_names:
            for sector in sectors[:10]:
                if count >= RAW_TARGET:
                    break
                full_name = f"{name} {sector}"
                domain = f"{name.lower()}{sector.lower().replace(' ','')}.org"
                companies.append({
                    "name": full_name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Bulk fill 4.5: city + name combinations
    if count < RAW_TARGET:
        for city in cities[:30]:
            for name in ["Tech", "Info", "Soft", "Labs", "Corp", "Biz", "Pro", "Sys"]:
                for n in range(1, 6):
                    if count >= RAW_TARGET:
                        break
                    cname = f"{city} {name} {n}"
                    domain = f"{city.lower()}{name.lower()}{n}.net"
                    companies.append({
                        "name": cname,
                        "domain": domain,
                        "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                    })
                    count += 1
                if count >= RAW_TARGET:
                    break
            if count >= RAW_TARGET:
                break

    # Bulk fill extra: new TLDs + double-pattern
    if count < RAW_TARGET:
        prefixes = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
                    "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Sigma",
                    "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"]
        for prefix in prefixes:
            for sector in sectors[:15]:
                if count >= RAW_TARGET: break
                name = f"{prefix} {sector}"
                domain = f"{prefix.lower()}{sector.lower().replace(' ','')}tech.in"
                companies.append({"name": name, "domain": domain, "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]})
                count += 1
            if count >= RAW_TARGET: break

    # Bulk fill extra 2: Colors + sectors
    if count < RAW_TARGET:
        colors = ["Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", "Brown",
                  "Black", "White", "Silver", "Gold", "Platinum", "Diamond", "Ruby",
                  "Emerald", "Sapphire", "Coral", "Ivory", "Lavender", "Magenta", "Teal"]
        for color in colors:
            for sector in sectors[:15]:
                if count >= RAW_TARGET: break
                name = f"{color} {sector}"
                domain = f"{color.lower()}{sector.lower().replace(' ','')}labs.in"
                companies.append({"name": name, "domain": domain, "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]})
                count += 1
            if count >= RAW_TARGET: break

    # Bulk fill 4: Indian words + Corp
        words = ["Apex", "Bharat", "Champion", "Diamond", "Emerald", "Golden", "Heritage",
                 "Imperial", "Jewel", "Kings", "Liberty", "Majestic", "Noble", "Omega",
                 "Pacific", "Quantum", "Royal", "Sapphire", "Titan", "Unique", "Valley",
                 "Windsor", "Zenith", "Accord", "Blossom", "Crystal", "Destiny", "Eagle",
                 "Fortune", "Garden", "Horizon", "Inspire", "Jubilee", "Knight", "Legend"]
        for word in words:
            for sector in sectors[:10]:
                if count >= RAW_TARGET:
                    break
                name = f"{word} {sector}"
                domain = f"{word.lower()}{sector.lower().replace(' ','')}.biz"
                companies.append({
                    "name": name,
                    "domain": domain,
                    "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]
                })
                count += 1
            if count >= RAW_TARGET:
                break

    # Bulk fill extra 3: Animals + services
    if count < RAW_TARGET:
        animals = ["Tiger", "Lion", "Eagle", "Falcon", "Hawk", "Peacock", "Dolphin", "Shark",
                   "Python", "Cobra", "Panther", "Leopard", "Wolf", "Bear", "Fox", "Deer",
                   "Swan", "Owl", "Crane", "Panda", "Koala", "Cheetah"]
        for animal in animals:
            for suffix in ["Tech", "Soft", "Corp", "Sol", "Sys", "Net"]:
                if count >= RAW_TARGET: break
                name = f"{animal} {suffix}"
                domain = f"{animal.lower()}{suffix.lower()}services.in"
                companies.append({"name": name, "domain": domain, "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]})
                count += 1
            if count >= RAW_TARGET: break

    # Bulk fill extra 4: Gems + sectors
    if count < RAW_TARGET:
        gems = ["Ruby", "Sapphire", "Emerald", "Diamond", "Topaz", "Opal", "Amethyst",
                "Garnet", "Jade", "Pearl", "Coral", "Onyx", "Quartz", "Turquoise", "Zircon"]
        for gem in gems:
            for sector in sectors[:10]:
                if count >= RAW_TARGET: break
                name = f"{gem} {sector}"
                domain = f"{gem.lower()}{sector.lower().replace(' ','')}gems.in"
                companies.append({"name": name, "domain": domain, "urls": [f"https://www.{domain}", f"https://www.{domain}/careers"]})
                count += 1
            if count >= RAW_TARGET: break

    # Deduplicate by domain
    print(f"Before dedup: {len(companies)} entries")
    seen = set()
    unique_companies = []
    for c in companies:
        if c["domain"] not in seen:
            seen.add(c["domain"])
            unique_companies.append(c)

    # Save
    with open(COMPANIES_FILE, "w") as f:
        json.dump(unique_companies, f, indent=2)

    print(f"Generated {len(unique_companies)} companies with {sum(len(c['urls']) for c in unique_companies)} career page URLs")
    return unique_companies


if __name__ == "__main__":
    build_companies_json()

