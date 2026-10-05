import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import re
from datetime import datetime


# ============================================================
# DATABASE
# ============================================================

DB_NAME = "ethio_emergency.db"


def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# ============================================================
# APPLICATION
# ============================================================

class EmergencySystem:

    def __init__(self, root):

        self.root = root
        self.root.geometry("1200x750")
        self.root.minsize(950, 650)

        self.language = "en"
        self.dark_mode = False

        self.current_user = None
        self.current_admin = None

        self.current_screen = self.show_home

        # ----------------------------------------------------
        # COLORS
        # ----------------------------------------------------

        self.light_colors = {
            "bg": "#F5F7FA",
            "white": "#FFFFFF",
            "dark": "#0D47A1",
            "text": "#17202A",
            "gray": "#607D8B",
            "red": "#D32F2F",
            "dark_red": "#B71C1C",
            "blue": "#1565C0",
            "dark_blue": "#0D47A1",
            "light_blue": "#E3F2FD",
            "light_red": "#FFEBEE",
            "green": "#2E7D32",
            "orange": "#EF6C00",
            "border": "#CFD8DC"
        }

        self.dark_colors = {
            "bg": "#121212",
            "white": "#1E1E1E",
            "dark": "#0A3D91",
            "text": "#F5F5F5",
            "gray": "#B0BEC5",
            "red": "#E53935",
            "dark_red": "#B71C1C",
            "blue": "#1E88E5",
            "dark_blue": "#0D47A1",
            "light_blue": "#18324A",
            "light_red": "#4A2020",
            "green": "#43A047",
            "orange": "#FB8C00",
            "border": "#37474F"
        }

        self.colors = self.light_colors.copy()

        # ----------------------------------------------------
        # LOCATIONS
        # Used in Create Account and Emergency Report
        # NOT displayed on the front page.
        # ----------------------------------------------------

        self.locations = [
            "Bole",
            "Kazanchis",
            "CMC",
            "Megenagna",
            "Gerji",
            "Sar Bet",
            "Piassa",
            "Arat Kilo",
            "Mexico",
            "Lideta",
            "Merkato",
            "Kolfe",
            "Jemo",
            "Ayat",
            "Summit",
            "Kirkos",
            "Nifas Silk",
            "Lafto",
            "Old Airport",
            "Yeka",
            "Gurd Shola",
            "Shiromeda",
            "4 Kilo",
            "Gotera",
            "Saris",
            "Akaki",
            "Lebu",
            "Kaliti",
            "Tor Hailoch",
            "Addis Ketema",
            "Ayer Tena",
            "Alem Bank",
            "Kera",
            "Sarawu",
            "Shola",
            "Haya Hulet",
            "Megenagna",
            "Wello Sefer",
            "Bambis",
            "Edna Mall",
            "Hayat",
            "CMC Michael",
            "Yerer",
            "Kotebe",
            "Summit Adebabay",
            "Mekanisa",
            "Alem Gena",
            "Sebeta",
            "Burayu",
            "Lege Tafo"
        ]

        # ----------------------------------------------------
        # EMERGENCY TYPES
        # ----------------------------------------------------

        self.emergency_types = [

            {
                "key": "medical",
                "en": "Medical Emergency",
                "am": "የሕክምና አደጋ",
                "description_en":
                    "A serious illness, injury, unconscious person, or medical condition requiring immediate help.",
                "description_am":
                    "ከባድ ህመም፣ ጉዳት፣ ራሱን የሳተ ሰው ወይም አስቸኳይ የሕክምና እርዳታ የሚፈልግ ሁኔታ።",
                "safety_en":
                    "Stay calm, keep the person safe and call emergency medical services.",
                "safety_am":
                    "ተረጋግተው ይቆዩ፣ ሰውየውን ከአደጋ ይጠብቁ እና የአስቸኳይ ሕክምና እርዳታ ይጠሩ።"
            },

            {
                "key": "police",
                "en": "Police Emergency",
                "am": "የፖሊስ አደጋ",
                "description_en":
                    "A situation involving crime, immediate danger, violence or a threat to public safety.",
                "description_am":
                    "ወንጀል፣ አስቸኳይ አደጋ፣ ጥቃት ወይም የህዝብ ደህንነትን የሚያሰጋ ሁኔታ።",
                "safety_en":
                    "Move to a safe place, avoid confrontation and contact the police.",
                "safety_am":
                    "ወደ ደህና ቦታ ይሂዱ፣ ከግጭት ይራቁ እና ፖሊስን ያነጋግሩ።"
            },

            {
                "key": "fire",
                "en": "Fire",
                "am": "እሳት",
                "description_en":
                    "A fire in a home, building, vehicle, business, forest or other area.",
                "description_am":
                    "በቤት፣ በህንፃ፣ በተሽከርካሪ፣ በንግድ ቦታ፣ በደን ወይም በሌላ ቦታ የተነሳ እሳት።",
                "safety_en":
                    "Leave the building immediately, stay away from smoke and call the fire service.",
                "safety_am":
                    "ህንፃውን ወዲያውኑ ለቀው ይውጡ፣ ከጭስ ይራቁ እና የእሳት አደጋ አገልግሎትን ይጠሩ።"
            },

            {
                "key": "traffic",
                "en": "Traffic Accident",
                "am": "የትራፊክ አደጋ",
                "description_en":
                    "A road accident involving vehicles, pedestrians or other road users.",
                "description_am":
                    "ተሽከርካሪዎችን፣ እግረኞችን ወይም ሌሎች የመንገድ ተጠቃሚዎችን ያካተተ የመንገድ አደጋ።",
                "safety_en":
                    "Move away from traffic if safe and call emergency services.",
                "safety_am":
                    "ደህንነቱ ከተጠበቀ ከትራፊክ ይራቁ እና የአስቸኳይ እርዳታ ይጠሩ።"
            },

            {
                "key": "car",
                "en": "Car Accident",
                "am": "የመኪና አደጋ",
                "description_en":
                    "A collision or serious accident involving one or more cars.",
                "description_am":
                    "አንድ ወይም ከዚያ በላይ መኪናዎችን ያካተተ ግጭት ወይም ከባድ አደጋ።",
                "safety_en":
                    "Move to a safe place if possible and do not stand in the road.",
                "safety_am":
                    "ከተቻለ ወደ ደህና ቦታ ይሂዱ እና በመንገድ ላይ አይቁሙ።"
            },

            {
                "key": "motorcycle",
                "en": "Motorcycle Accident",
                "am": "የሞተር ሳይክል አደጋ",
                "description_en":
                    "An accident involving a motorcycle and another vehicle, object or person.",
                "description_am":
                    "ሞተር ሳይክልን እና ሌላ ተሽከርካሪ፣ ነገር ወይም ሰው ያካተተ አደጋ።",
                "safety_en":
                    "Do not remove a seriously injured rider's helmet unless necessary for breathing.",
                "safety_am":
                    "ከባድ ጉዳት ካለ የሞተር ሳይክል ተጠቃሚውን የራስ ቁር ካስፈለገ በስተቀር አያውልቁ።"
            },

            {
                "key": "pedestrian",
                "en": "Pedestrian Accident",
                "am": "የእግረኛ አደጋ",
                "description_en":
                    "An accident in which a pedestrian is hit or injured by a vehicle.",
                "description_am":
                    "እግረኛ በተሽከርካሪ የተመታበት ወይም የተጎዳበት አደጋ።",
                "safety_en":
                    "Keep the injured person safe from traffic and call medical assistance.",
                "safety_am":
                    "የተጎዳውን ሰው ከትራፊክ ይጠብቁ እና የሕክምና እርዳታ ይጠሩ።"
            },

            {
                "key": "bus",
                "en": "Bus Accident",
                "am": "የአውቶቡስ አደጋ",
                "description_en":
                    "An accident involving a public or private bus.",
                "description_am":
                    "የህዝብ ወይም የግል አውቶቡስን ያካተተ አደጋ።",
                "safety_en":
                    "Move away from damaged vehicles and report injuries immediately.",
                "safety_am":
                    "ከተጎዳው ተሽከርካሪ ይራቁ እና ጉዳቶች ካሉ ወዲያውኑ ያሳውቁ።"
            },

            {
                "key": "truck",
                "en": "Truck Accident",
                "am": "የጭነት መኪና አደጋ",
                "description_en":
                    "An accident involving a truck or heavy transport vehicle.",
                "description_am":
                    "ጭነት መኪና ወይም ከባድ የማጓጓዣ ተሽከርካሪን ያካተተ አደጋ።",
                "safety_en":
                    "Stay away from the truck, especially if fuel or dangerous materials may be involved.",
                "safety_am":
                    "ከጭነት መኪናው ይራቁ፣ በተለይ ነዳጅ ወይም አደገኛ እቃ ካለ።"
            },

            {
                "key": "taxi",
                "en": "Taxi Accident",
                "am": "የታክሲ አደጋ",
                "description_en":
                    "An accident involving a taxi or taxi passenger.",
                "description_am":
                    "ታክሲ ወይም የታክሲ ተሳፋሪን ያካተተ አደጋ።",
                "safety_en":
                    "Move away from traffic and request medical or police assistance.",
                "safety_am":
                    "ከትራፊክ ይራቁ እና የሕክምና ወይም የፖሊስ እርዳታ ይጠይቁ።"
            },

            {
                "key": "train",
                "en": "Train Accident",
                "am": "የባቡር አደጋ",
                "description_en":
                    "An accident involving a train, railway or train passengers.",
                "description_am":
                    "ባቡር፣ የባቡር መስመር ወይም የባቡር ተሳፋሪዎችን ያካተተ አደጋ።",
                "safety_en":
                    "Stay away from railway tracks and damaged equipment.",
                "safety_am":
                    "ከባቡር መስመሮችና ከተጎዱ መሳሪያዎች ይራቁ።"
            },

            {
                "key": "airplane",
                "en": "Airplane Accident",
                "am": "የአውሮፕላን አደጋ",
                "description_en":
                    "An accident involving an airplane or aircraft.",
                "description_am":
                    "አውሮፕላን ወይም ሌላ አየር ተሽከርካሪን ያካተተ አደጋ።",
                "safety_en":
                    "Stay away from the aircraft and follow instructions from emergency responders.",
                "safety_am":
                    "ከአውሮፕላኑ ይራቁ እና የአስቸኳይ ሰራተኞችን መመሪያ ይከተሉ።"
            },

            {
                "key": "home",
                "en": "Home Emergency",
                "am": "የቤት አደጋ",
                "description_en":
                    "An emergency occurring inside or around a residential home.",
                "description_am":
                    "በመኖሪያ ቤት ውስጥ ወይም በአካባቢው የሚከሰት አስቸኳይ ሁኔታ።",
                "safety_en":
                    "Keep family members away from danger and contact the appropriate service.",
                "safety_am":
                    "የቤተሰብ አባላትን ከአደጋው ያርቁ እና ተገቢውን አገልግሎት ያነጋግሩ።"
            },

            {
                "key": "flood",
                "en": "Flood",
                "am": "ጎርፍ",
                "description_en":
                    "Flooding caused by heavy rain, overflowing rivers or drainage problems.",
                "description_am":
                    "በከባድ ዝናብ፣ በወንዝ መሙላት ወይም በፍሳሽ ችግር የሚከሰት ጎርፍ።",
                "safety_en":
                    "Move to higher ground and avoid moving floodwater.",
                "safety_am":
                    "ወደ ከፍ ያለ ቦታ ይሂዱ እና በጎርፍ ውሃ ውስጥ አይጓዙ።"
            },

            {
                "key": "earthquake",
                "en": "Earthquake",
                "am": "የመሬት መንቀጥቀጥ",
                "description_en":
                    "Ground shaking that may cause building damage, falling objects or injuries.",
                "description_am":
                    "የህንፃ ጉዳት፣ የነገሮች መውደቅ ወይም ጉዳት ሊያመጣ የሚችል የመሬት መንቀጥቀጥ።",
                "safety_en":
                    "Drop, cover and hold on. Stay away from windows.",
                "safety_am":
                    "ዝቅ ይበሉ፣ ራስዎን ይሸፍኑ እና ይያዙ። ከመስኮቶች ይራቁ።"
            },

            {
                "key": "missing",
                "en": "Missing Person",
                "am": "የጠፋ ሰው",
                "description_en":
                    "A person who cannot be located and may require assistance.",
                "description_am":
                    "የት እንዳለ የማይታወቅ እና እርዳታ ሊፈልግ የሚችል ሰው።",
                "safety_en":
                    "Provide accurate information, recent photo or description and last known location.",
                "safety_am":
                    "ትክክለኛ መረጃ፣ የቅርብ ጊዜ ፎቶ ወይም መግለጫ እና የመጨረሻ የታየበትን ቦታ ያቅርቡ።"
            },

            {
                "key": "theft",
                "en": "Theft / Robbery",
                "am": "ስርቆት / ዝርፊያ",
                "description_en":
                    "The theft of property or robbery involving a threat or use of force.",
                "description_am":
                    "ንብረት መስረቅ ወይም በማስፈራራት ወይም በኃይል የሚፈጸም ዝርፊያ።",
                "safety_en":
                    "Do not confront the suspect. Move to a safe location and contact police.",
                "safety_am":
                    "ከተጠርጣሪው ጋር አይጋጩ። ወደ ደህና ቦታ ይሂዱ እና ፖሊስን ያነጋግሩ።"
            },

            {
                "key": "violence",
                "en": "Violence / Assault",
                "am": "ጥቃት / የኃይል አደጋ",
                "description_en":
                    "Physical violence, assault, fighting or an immediate threat to safety.",
                "description_am":
                    "አካላዊ ጥቃት፣ ድብደባ፣ ግጭት ወይም የደህንነት አስቸኳይ ስጋት።",
                "safety_en":
                    "Move away from the attacker and contact police or emergency services.",
                "safety_am":
                    "ከአጥቂው ይራቁ እና ፖሊስን ወይም የአስቸኳይ እርዳታን ይጠሩ።"
            },

            {
                "key": "gas",
                "en": "Gas Leak",
                "am": "የጋዝ መፍሰስ",
                "description_en":
                    "A suspected leak of cooking gas or another dangerous gas.",
                "description_am":
                    "የምግብ ማብሰያ ጋዝ ወይም ሌላ አደገኛ ጋዝ መፍሰስ።",
                "safety_en":
                    "Do not use flames or electrical switches. Leave the area and call for help.",
                "safety_am":
                    "እሳት ወይም የኤሌክትሪክ ማብሪያ አይጠቀሙ። አካባቢውን ለቀው እርዳታ ይጠይቁ።"
            },

            {
                "key": "collapse",
                "en": "Building Collapse",
                "am": "የህንፃ መፍረስ",
                "description_en":
                    "A building, wall or structure has collapsed or is at risk of collapsing.",
                "description_am":
                    "ህንፃ፣ ግድግዳ ወይም ሌላ መዋቅር የፈረሰ ወይም ሊፈርስ የተቃረበ ሁኔታ።",
                "safety_en":
                    "Stay away from unstable structures and do not enter the damaged area.",
                "safety_am":
                    "ከማይረጋጉ መዋቅሮች ይራቁ እና ወደ ተበላሸው ቦታ አይግቡ።"
            },

            {
                "key": "road_blockage",
                "en": "Road Blockage",
                "am": "የመንገድ መዘጋት",
                "description_en":
                    "A road is blocked because of an accident, debris, construction or another emergency.",
                "description_am":
                    "በአደጋ፣ በፍርስራሽ፣ በግንባታ ወይም በሌላ አደጋ ምክንያት መንገድ መዘጋት።",
                "safety_en":
                    "Avoid the blocked road and use an alternative safe route.",
                "safety_am":
                    "የተዘጋውን መንገድ ያስወግዱ እና ሌላ ደህና መንገድ ይጠቀሙ።"
            },

            {
                "key": "electrical",
                "en": "Electrical Emergency",
                "am": "የኤሌክትሪክ አደጋ",
                "description_en":
                    "Exposed wires, electrical fire, electric shock or another electrical hazard.",
                "description_am":
                    "የተጋለጡ ሽቦዎች፣ የኤሌክትሪክ እሳት፣ የኤሌክትሪክ ንክኪ ወይም ሌላ የኤሌክትሪክ አደጋ።",
                "safety_en":
                    "Do not touch exposed wires. Keep away and contact qualified emergency services.",
                "safety_am":
                    "የተጋለጡ ሽቦዎችን አይንኩ። ከአካባቢው ይራቁ እና ባለሙያ እርዳታ ይጠይቁ።"
            },

            {
                "key": "water",
                "en": "Water Emergency",
                "am": "የውሃ አደጋ",
                "description_en":
                    "A dangerous water-related incident such as drowning or a serious water hazard.",
                "description_am":
                    "እንደ መስጠም ወይም ከባድ የውሃ አደጋ ያለ ሁኔታ።",
                "safety_en":
                    "Do not enter dangerous water to rescue someone unless you are trained.",
                "safety_am":
                    "ሰውን ለማዳን ስልጠና ከሌለዎት ወደ አደገኛ ውሃ አይግቡ።"
            },

            {
                "key": "drowning",
                "en": "Drowning / Water Accident",
                "am": "የመስጠም / የውሃ አደጋ",
                "description_en":
                    "A person is drowning or has been involved in a serious water-related accident.",
                "description_am":
                    "ሰው በውሃ ውስጥ እየሰመጠ ወይም በከባድ የውሃ አደጋ ውስጥ የገባ ሁኔታ።",
                "safety_en":
                    "Call for help and use a safe rescue method. Do not enter dangerous water without training.",
                "safety_am":
                    "እርዳታ ይጠይቁ እና ደህና የማዳኛ ዘዴ ይጠቀሙ። ስልጠና ከሌለ ወደ አደገኛ ውሃ አይግቡ።"
            },

            {
                "key": "industrial",
                "en": "Industrial Accident",
                "am": "የኢንዱስትሪ አደጋ",
                "description_en":
                    "An accident involving factories, industrial machinery, workers or industrial materials.",
                "description_am":
                    "ፋብሪካ፣ የኢንዱስትሪ ማሽን፣ ሰራተኞች ወይም የኢንዱስትሪ እቃዎችን ያካተተ አደጋ።",
                "safety_en":
                    "Leave the danger area and follow workplace emergency procedures.",
                "safety_am":
                    "ከአደጋው ቦታ ይራቁ እና የስራ ቦታውን የአስቸኳይ ጊዜ ሂደት ይከተሉ።"
            },

            {
                "key": "explosion",
                "en": "Explosion",
                "am": "ፍንዳታ",
                "description_en":
                    "An explosion involving gas, fuel, chemicals, buildings, vehicles or other materials.",
                "description_am":
                    "ጋዝ፣ ነዳጅ፣ ኬሚካል፣ ህንፃ፣ ተሽከርካሪ ወይም ሌላ ነገር የሚያካትት ፍንዳታ።",
                "safety_en":
                    "Move away from the area immediately and avoid fire, sparks and damaged structures.",
                "safety_am":
                    "ወዲያውኑ ከአካባቢው ይራቁ፣ ከእሳት፣ ከብልጭታ እና ከተበላሹ መዋቅሮች ይጠንቀቁ።"
            },

            {
                "key": "construction",
                "en": "Construction Accident",
                "am": "የግንባታ አደጋ",
                "description_en":
                    "An accident involving construction workers, machinery or construction materials.",
                "description_am":
                    "የግንባታ ሰራተኞችን፣ ማሽኖችን ወይም የግንባታ እቃዎችን ያካተተ አደጋ።",
                "safety_en":
                    "Stay outside the danger zone and keep away from machinery and falling materials.",
                "safety_am":
                    "ከአደጋው ቦታ ይራቁ፣ ከማሽኖችና ከሚወድቁ እቃዎች ይጠንቀቁ።"
            },

            {
                "key": "hit_run",
                "en": "Hit and Run",
                "am": "አደጋ አድርሶ መሰወር",
                "description_en":
                    "A vehicle causes an accident and leaves the scene without stopping.",
                "description_am":
                    "ተሽከርካሪ አደጋ ካደረሰ በኋላ ሳይቆም ከቦታው የሚሰወርበት ሁኔታ።",
                "safety_en":
                    "Do not chase the vehicle. Record useful details if safe and contact police.",
                "safety_am":
                    "ተሽከርካሪውን አትከታተሉ። ደህና ከሆነ መረጃውን ይመዝግቡ እና ፖሊስን ያነጋግሩ።"
            },

            {
                "key": "falling_object",
                "en": "Falling Object Accident",
                "am": "የወደቀ ነገር አደጋ",
                "description_en":
                    "An accident caused by a falling object, material or structure.",
                "description_am":
                    "በሚወድቅ ነገር፣ እቃ ወይም መዋቅር የሚከሰት አደጋ።",
                "safety_en":
                    "Move away from the area and avoid standing beneath unstable objects.",
                "safety_am":
                    "ከአካባቢው ይራቁ እና ከማይረጋጉ ነገሮች ስር አይቁሙ።"
            },

            {
                "key": "other",
                "en": "Other Emergency",
                "am": "ሌላ አደጋ",
                "description_en":
                    "Any emergency that does not match the listed emergency categories.",
                "description_am":
                    "ከተዘረዘሩት የአደጋ ምድቦች ውጭ የሆነ ማንኛውም አስቸኳይ ሁኔታ።",
                "safety_en":
                    "Move to a safe place and contact the appropriate emergency service.",
                "safety_am":
                    "ወደ ደህና ቦታ ይሂዱ እና ተገቢውን የአስቸኳይ አገልግሎት ያነጋግሩ።"
            }
        ]

        # ----------------------------------------------------
        # TRANSLATIONS
        # ----------------------------------------------------

        self.translations = {

            "en": {
                "app_title": "Ethio Emergency Response and Management System",
                "home": "Home",
                "create_account": "Create Account",
                "user_login": "User Login",
                "administrator": "Administrator",
                "emergency_contacts": "Emergency Contacts",
                "emergency_types": "Emergency Types",
                "report_emergency": "Report Emergency",
                "logout": "Logout",
                "dashboard": "Dashboard",
                "my_reports": "My Reports",
                "my_profile": "My Profile",
                "manage_users": "Manage Users",
                "manage_reports": "Manage Reports",
                "manage_contacts": "Manage Contacts",
                "full_name": "Full Name",
                "age": "Age",
                "gender": "Gender",
                "phone": "Phone",
                "email": "Email",
                "address": "Address",
                "username": "Username",
                "password": "Password",
                "confirm_password": "Confirm Password",
                "emergency_contact": "Emergency Contact",
                "emergency_type": "Emergency Type",
                "location": "Location",
                "exact_location": "Please give the exact location",
                "description": "Description",
                "people_affected": "People Affected",
                "priority": "Priority",
                "status": "Status",
                "login": "Login",
                "register": "Register",
                "back": "Back",
                "submit": "Submit",
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "close": "Close",
                "search": "Search",
                "actions": "Actions",
                "male": "Male",
                "female": "Female",
                "other_gender": "Other",
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                "pending": "Pending",
                "in_progress": "In Progress",
                "resolved": "Resolved",
                "no_reports": "No reports found.",
                "dark_mode": "Dark Mode",
                "light_mode": "Light Mode",
                "language": "Language",
                "welcome": "Welcome",
                "safety_rule": "Safety Rule",
                "details": "Details",
                "view_details": "View Details",
                "admin_login": "Administrator Login",
                "admin_dashboard": "Administrator Dashboard",
                "total_users": "Total Users",
                "total_reports": "Total Reports",
                "pending_reports": "Pending Reports",
                "resolved_reports": "Resolved Reports",
                "required": "Please fill in all required fields.",
                "password_mismatch": "Passwords do not match.",
                "login_failed": "Invalid username or password.",
                "account_created": "Account created successfully.",
                "report_created": "Emergency report submitted successfully.",
                "confirm_delete": "Are you sure you want to delete this?",
                "user_deleted": "User deleted successfully.",
                "report_deleted": "Report deleted successfully.",
                "admin": "Administrator",
                "user": "User",
                "select": "Select",
                "refresh": "Refresh",
                "call_now": "Call Now",
                "dialer_message": "Go to your phone dialer.",
                "invalid": "Invalid information. Please check your input.",
                "home_subtitle": "Smart emergency reporting and response system",
                "home_description": "Report emergencies quickly and help connect people with the right emergency service.",
                "create_account_desc": "Create your emergency response account",
                "login_desc": "Login and manage your emergency reports",
                "admin_desc": "Administrator management system",
                "contacts_desc": "Important emergency service contacts",
                "emergency_select_desc": "Select the emergency type that best describes your situation.",
                "footer": "Ethio Emergency Response System",
                "login_subtitle": "Login to your emergency response account",
                "report_subtitle": "Send an emergency report",
                "reports_subtitle": "View your emergency reports",
                "profile_subtitle": "Your account information",
                "admin_access": "Administrator access",
                "quick_actions": "Quick Actions",
                "users_subtitle": "Manage registered users",
                "reports_manage_subtitle": "Manage emergency reports",
                "contacts_subtitle": "Use the appropriate emergency service when needed.",
                "contacts_manage_subtitle": "Manage emergency service contacts",
                "add_contact": "Add Emergency Contact",
                "select_user": "Please select a user.",
                "select_report": "Please select a report.",
                "select_contact": "Please select a contact.",
                "warning": "Warning",
                "error": "Error",
                "success": "Success",
                "confirm": "Confirm",
                "service": "Service",
                "date": "Date",
                "id": "ID",
                "username_exists": "Username already exists.",
                "manage_info_desc": "Manage your emergency information and reports.",
                "report_warning": "If you are experiencing an emergency, report it immediately."
            },

            "am": {
                "app_title": "የኢትዮ የአስቸኳይ ጊዜ ምላሽና አስተዳደር ስርዓት",
                "home": "መነሻ",
                "create_account": "መለያ ፍጠር",
                "user_login": "የተጠቃሚ መግቢያ",
                "administrator": "አስተዳዳሪ",
                "emergency_contacts": "የአስቸኳይ ጊዜ እውቂያዎች",
                "emergency_types": "የአደጋ አይነቶች",
                "report_emergency": "አደጋ ሪፖርት አድርግ",
                "logout": "ውጣ",
                "dashboard": "ዳሽቦርድ",
                "my_reports": "ሪፖርቶቼ",
                "my_profile": "መገለጫዬ",
                "manage_users": "ተጠቃሚዎችን አስተዳድር",
                "manage_reports": "ሪፖርቶችን አስተዳድር",
                "manage_contacts": "እውቂያዎችን አስተዳድር",
                "full_name": "ሙሉ ስም",
                "age": "ዕድሜ",
                "gender": "ጾታ",
                "phone": "ስልክ",
                "email": "ኢሜይል",
                "address": "አድራሻ",
                "username": "የተጠቃሚ ስም",
                "password": "የይለፍ ቃል",
                "confirm_password": "የይለፍ ቃል አረጋግጥ",
                "emergency_contact": "የአስቸኳይ ጊዜ እውቂያ",
                "emergency_type": "የአደጋ አይነት",
                "location": "ቦታ",
                "exact_location": "እባክዎ ትክክለኛውን ቦታ ይግለጹ",
                "description": "መግለጫ",
                "people_affected": "የተጎዱ ሰዎች",
                "priority": "ቅድሚያ",
                "status": "ሁኔታ",
                "login": "ግባ",
                "register": "ተመዝገብ",
                "back": "ተመለስ",
                "submit": "ላክ",
                "save": "አስቀምጥ",
                "cancel": "ሰርዝ",
                "delete": "ሰርዝ",
                "close": "ዝጋ",
                "search": "ፈልግ",
                "actions": "ተግባራት",
                "male": "ወንድ",
                "female": "ሴት",
                "other_gender": "ሌላ",
                "high": "ከፍተኛ",
                "medium": "መካከለኛ",
                "low": "ዝቅተኛ",
                "pending": "በመጠባበቅ ላይ",
                "in_progress": "በሂደት ላይ",
                "resolved": "ተፈቷል",
                "no_reports": "ምንም ሪፖርት አልተገኘም።",
                "dark_mode": "ጨለማ ሁነታ",
                "light_mode": "ብርሃን ሁነታ",
                "language": "ቋንቋ",
                "welcome": "እንኳን ደህና መጡ",
                "safety_rule": "የደህንነት መመሪያ",
                "details": "ዝርዝር",
                "view_details": "ዝርዝር ይመልከቱ",
                "admin_login": "የአስተዳዳሪ መግቢያ",
                "admin_dashboard": "የአስተዳዳሪ ዳሽቦርድ",
                "total_users": "ጠቅላላ ተጠቃሚዎች",
                "total_reports": "ጠቅላላ ሪፖርቶች",
                "pending_reports": "በመጠባበቅ ላይ ያሉ",
                "resolved_reports": "የተፈቱ",
                "required": "እባክዎ ሁሉንም አስፈላጊ መስኮች ይሙሉ።",
                "password_mismatch": "የይለፍ ቃሎች አይመሳሰሉም።",
                "login_failed": "የተሳሳተ የተጠቃሚ ስም ወይም የይለፍ ቃል።",
                "account_created": "መለያው በተሳካ ሁኔታ ተፈጥሯል።",
                "report_created": "የአደጋ ሪፖርቱ በተሳካ ሁኔታ ተልኳል።",
                "confirm_delete": "ይህን ለመሰረዝ እርግጠኛ ነዎት?",
                "user_deleted": "ተጠቃሚው ተሰርዟል።",
                "report_deleted": "ሪፖርቱ ተሰርዟል።",
                "admin": "አስተዳዳሪ",
                "user": "ተጠቃሚ",
                "select": "ይምረጡ",
                "refresh": "አድስ",
                "call_now": "አሁን ይደውሉ",
                "dialer_message": "ወደ ስልክዎ መደወያ ይሂዱ።",
                "invalid": "የተሳሳተ መረጃ ነው። እባክዎ መረጃዎን ያረጋግጡ።",
                "home_subtitle": "ብልህ የአደጋ ሪፖርትና ምላሽ ስርዓት",
                "home_description": "አደጋዎችን በፍጥነት ሪፖርት ያድርጉ እና ሰዎችን ከተገቢው የአስቸኳይ አገልግሎት ጋር ያገናኙ።",
                "create_account_desc": "የአስቸኳይ ጊዜ ምላሽ መለያዎን ይፍጠሩ",
                "login_desc": "ይግቡ እና የአደጋ ሪፖርቶችዎን ያስተዳድሩ",
                "admin_desc": "የአስተዳዳሪ አስተዳደር ስርዓት",
                "contacts_desc": "አስፈላጊ የአስቸኳይ ጊዜ አገልግሎት እውቂያዎች",
                "emergency_select_desc": "ሁኔታዎን በተሻለ የሚገልጸውን የአደጋ አይነት ይምረጡ።",
                "footer": "የኢትዮ የአስቸኳይ ጊዜ ምላሽ ስርዓት",
                "login_subtitle": "ወደ የአስቸኳይ ጊዜ ምላሽ መለያዎ ይግቡ",
                "report_subtitle": "የአደጋ ሪፖርት ይላኩ",
                "reports_subtitle": "የአደጋ ሪፖርቶችዎን ይመልከቱ",
                "profile_subtitle": "የመለያዎ መረጃ",
                "admin_access": "የአስተዳዳሪ መዳረሻ",
                "quick_actions": "ፈጣን ተግባራት",
                "users_subtitle": "የተመዘገቡ ተጠቃሚዎችን ያስተዳድሩ",
                "reports_manage_subtitle": "የአደጋ ሪፖርቶችን ያስተዳድሩ",
                "contacts_subtitle": "በሚያስፈልግበት ጊዜ ተገቢውን የአስቸኳይ ጊዜ አገልግሎት ይጠቀሙ።",
                "contacts_manage_subtitle": "የአስቸኳይ ጊዜ አገልግሎት እውቂያዎችን ያስተዳድሩ",
                "add_contact": "የአስቸኳይ ጊዜ እውቂያ ያክሉ",
                "select_user": "እባክዎ ተጠቃሚ ይምረጡ።",
                "select_report": "እባክዎ ሪፖርት ይምረጡ።",
                "select_contact": "እባክዎ እውቂያ ይምረጡ።",
                "warning": "ማስጠንቀቂያ",
                "error": "ስህተት",
                "success": "ተሳክቷል",
                "confirm": "ማረጋገጫ",
                "service": "አገልግሎት",
                "date": "ቀን",
                "id": "መለያ ቁጥር",
                "username_exists": "ይህ የተጠቃሚ ስም አስቀድሞ አለ።",
                "manage_info_desc": "የአስቸኳይ ጊዜ መረጃዎንና ሪፖርቶችዎን ያስተዳድሩ።",
                "report_warning": "አስቸኳይ ሁኔታ ካጋጠመዎት ወዲያውኑ ሪፖርት ያድርጉ።"
            }
        }

        self.root.title(self.t("app_title"))

        # ----------------------------------------------------
        # DATABASE
        # ----------------------------------------------------

        self.initialize_database()

        # ----------------------------------------------------
        # STYLE
        # ----------------------------------------------------

        self.setup_styles()

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        self.show_home()

    # ========================================================
    # TRANSLATION
    # ========================================================

    def t(self, key):
        return self.translations[self.language].get(key, key)

    def emergency_name(self, item):
        return item["en"] if self.language == "en" else item["am"]

    def emergency_description(self, item):
        if self.language == "en":
            return item["description_en"]
        return item["description_am"]

    def emergency_safety(self, item):
        if self.language == "en":
            return item["safety_en"]
        return item["safety_am"]

    def get_emergency_names(self):
        return [self.emergency_name(x) for x in self.emergency_types]

    def display_priority(self, value):
        if self.language == "am":
            return {"High": "ከፍተኛ", "Medium": "መካከለኛ", "Low": "ዝቅተኛ"}.get(value, value)
        return value

    def display_status(self, value):
        if self.language == "am":
            return {"Pending": "በመጠባበቅ ላይ", "In Progress": "በሂደት ላይ", "Resolved": "ተፈቷል"}.get(value, value)
        return value

    def display_contact(self, service, description):
        if self.language == "am":
            services = {"Police":"ፖሊስ", "Fire & Emergency":"እሳት እና አስቸኳይ አገልግሎት", "Ambulance":"አምቡላንስ", "Federal Police":"ፌዴራል ፖሊስ", "Traffic Police":"ትራፊክ ፖሊስ"}
            desc = {"Police emergency service":"የፖሊስ አስቸኳይ አገልግሎት", "Fire and emergency response":"የእሳት እና የአስቸኳይ ጊዜ ምላሽ", "Emergency medical assistance":"የአስቸኳይ ሕክምና እርዳታ", "Federal police emergency service":"የፌዴራል ፖሊስ አስቸኳይ አገልግሎት", "Traffic accident assistance":"የትራፊክ አደጋ እርዳታ"}
            return services.get(service, service), desc.get(description, description)
        return service, description

    def display_location(self, value):
        if self.language == "am":
            return {
                "Bole":"ቦሌ", "Kazanchis":"ካዛንቺስ", "CMC":"ሲኤምሲ", "Megenagna":"መገናኛ", "Gerji":"ገርጂ",
                "Sar Bet":"ሳር ቤት", "Piassa":"ፒያሳ", "Arat Kilo":"አራት ኪሎ", "Mexico":"ሜክሲኮ", "Lideta":"ልደታ",
                "Merkato":"መርካቶ", "Kolfe":"ኮልፌ", "Jemo":"ጀሞ", "Ayat":"አያት", "Summit":"ሰሚት", "Kirkos":"ቂርቆስ",
                "Nifas Silk":"ንፋስ ስልክ", "Lafto":"ላፍቶ", "Old Airport":"አሮጌ አየር ማረፊያ", "Yeka":"የካ",
                "Gurd Shola":"ጉርድ ሾላ", "Shiromeda":"ሽሮ ሜዳ", "4 Kilo":"አራት ኪሎ", "Gotera":"ጎተራ", "Saris":"ሳሪስ",
                "Akaki":"አቃቂ", "Lebu":"ለቡ", "Kaliti":"ቃሊቲ", "Tor Hailoch":"ቶር ሃይሎች", "Addis Ketema":"አዲስ ከተማ",
                "Ayer Tena":"አየር ጤና", "Alem Bank":"አለም ባንክ", "Kera":"ከራ", "Sarawu":"ሳራዎ", "Shola":"ሾላ",
                "Haya Hulet":"ሃያ ሁለት", "Wello Sefer":"ወሎ ሰፈር", "Bambis":"ባምቢስ", "Edna Mall":"ኤድና ሞል", "Hayat":"ሃያት",
                "CMC Michael":"ሲኤምሲ ሚካኤል", "Yerer":"የረር", "Kotebe":"ኮተቤ", "Summit Adebabay":"ሰሚት አደባባይ",
                "Mekanisa":"መካኒሳ", "Alem Gena":"አለም ገና", "Sebeta":"ሰበታ", "Burayu":"ቡራዩ", "Lege Tafo":"ለገ ጣፎ"
            }.get(value, value)
        return value

    def get_emergency_db_value(self, displayed_name):
        for item in self.emergency_types:
            if displayed_name == item["en"] or displayed_name == item["am"]:
                return item["en"]

        return displayed_name

    def get_emergency_display_name(self, database_name):
        for item in self.emergency_types:
            if database_name == item["en"]:
                return self.emergency_name(item)

        return database_name

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    def initialize_database(self):

        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                emergency_contact TEXT,
                created_at TEXT
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS emergency_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                emergency_type TEXT,
                location TEXT,
                description TEXT,
                people_affected INTEGER,
                priority TEXT,
                status TEXT DEFAULT 'Pending',
                created_at TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
                    ON DELETE CASCADE
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS emergency_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service TEXT,
                phone TEXT,
                description TEXT
            )
        """)

        # ----------------------------------------------------
        # DATABASE MIGRATION
        # Add emergency_type to old users table
        # ----------------------------------------------------

        columns = [
            row["name"]
            for row in cur.execute("PRAGMA table_info(users)").fetchall()
        ]

        if "emergency_type" not in columns:
            cur.execute(
                "ALTER TABLE users ADD COLUMN emergency_type TEXT"
            )

        # ----------------------------------------------------
        # DEFAULT ADMIN
        # ----------------------------------------------------

        admin = cur.execute(
            "SELECT * FROM admins WHERE username = ?",
            ("admin",)
        ).fetchone()

        if not admin:
            cur.execute("""
                INSERT INTO admins (username, password)
                VALUES (?, ?)
            """, (
                "admin",
                hash_password("admin123")
            ))

        # ----------------------------------------------------
        # EMERGENCY CONTACTS
        # ----------------------------------------------------

        count = cur.execute(
            "SELECT COUNT(*) AS total FROM emergency_contacts"
        ).fetchone()["total"]

        if count == 0:

            contacts = [
                (
                    "Police",
                    "991",
                    "Police emergency service"
                ),
                (
                    "Fire & Emergency",
                    "939",
                    "Fire and emergency response"
                ),
                (
                    "Ambulance",
                    "907",
                    "Emergency medical assistance"
                ),
                (
                    "Federal Police",
                    "991",
                    "Federal police emergency service"
                ),
                (
                    "Traffic Police",
                    "991",
                    "Traffic accident assistance"
                )
            ]

            cur.executemany("""
                INSERT INTO emergency_contacts
                (service, phone, description)
                VALUES (?, ?, ?)
            """, contacts)

        conn.commit()
        conn.close()

    # ========================================================
    # STYLE
    # ========================================================

    def setup_styles(self):

        self.style = ttk.Style()

        try:
            self.style.theme_use("clam")
        except:
            pass

        self.style.configure(
            "TCombobox",
            fieldbackground=self.colors["white"],
            background=self.colors["white"],
            foreground=self.colors["text"],
            arrowcolor=self.colors["blue"]
        )

        self.style.map(
            "TCombobox",
            fieldbackground=[
                ("readonly", self.colors["white"])
            ],
            foreground=[
                ("readonly", self.colors["text"])
            ]
        )

        self.style.configure(
            "Treeview",
            background=self.colors["white"],
            foreground=self.colors["text"],
            fieldbackground=self.colors["white"],
            rowheight=35,
            borderwidth=0
        )

        self.style.configure(
            "Treeview.Heading",
            background=self.colors["dark_blue"],
            foreground="white",
            font=("Arial", 10, "bold")
        )

        self.style.map(
            "Treeview",
            background=[
                ("selected", self.colors["blue"])
            ],
            foreground=[
                ("selected", "white")
            ]
        )

    # ========================================================
    # THEME
    # ========================================================

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.colors = self.dark_colors.copy()
        else:
            self.colors = self.light_colors.copy()

        self.setup_styles()

        if self.current_screen:
            self.current_screen()

    # ========================================================
    # NAVIGATION / REFRESH / CALL HELPERS
    # ========================================================

    def go_back(self):
        # Back never logs the active account out.
        if self.current_user:
            self.user_dashboard()
        elif self.current_admin:
            self.admin_dashboard()
        else:
            self.show_home()

    def refresh_screen(self):
        # Rebuild the current screen from the permanent SQLite database.
        if self.current_screen:
            self.current_screen()

    def show_dialer_message(self):
        messagebox.showinfo(self.t("call_now"), self.t("dialer_message"))

    def invalid(self):
        messagebox.showerror(self.t("invalid"), self.t("invalid"))

    # ========================================================
    # CLEAR SCREEN
    # ========================================================

    def clear_screen(self):

        for widget in self.root.winfo_children():
            widget.destroy()

    # ========================================================
    # SCROLLABLE FRAME
    # ========================================================

    def create_scrollable_frame(self):

        outer = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        outer.pack(
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            outer,
            bg=self.colors["bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        content = tk.Frame(
            canvas,
            bg=self.colors["bg"]
        )

        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        def configure(event):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        content.bind(
            "<Configure>",
            configure
        )

        def resize(event):
            canvas.itemconfig(
                window_id,
                width=event.width
            )

        canvas.bind(
            "<Configure>",
            resize
        )

        def mousewheel(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        canvas.bind_all(
            "<MouseWheel>",
            mousewheel
        )

        return content

    # ========================================================
    # HEADER
    # ========================================================

    def create_header(
        self,
        title=None,
        subtitle=None,
        show_back=False
    ):

        header = tk.Frame(
            self.root,
            bg=self.colors["dark_blue"],
            height=85
        )

        header.pack(
            fill="x"
        )

        header.pack_propagate(False)

        # Left red strip
        tk.Frame(
            header,
            bg=self.colors["red"],
            width=8
        ).pack(
            side="left",
            fill="y"
        )

        # Title area
        title_frame = tk.Frame(
            header,
            bg=self.colors["dark_blue"]
        )

        title_frame.pack(
            side="left",
            fill="both",
            expand=True,
            padx=20
        )

        if title is None:
            title = self.t("app_title")

        tk.Label(
            title_frame,
            text=title,
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 19, "bold"),
            anchor="w"
        ).pack(
            pady=(15, 0),
            anchor="w"
        )

        if subtitle:

            tk.Label(
                title_frame,
                text=subtitle,
                bg=self.colors["dark_blue"],
                fg="#DCE8F7",
                font=("Arial", 9),
                anchor="w"
            ).pack(
                anchor="w"
            )

        # Theme button

        theme_text = (
            "☀ " + self.t("light_mode")
            if self.dark_mode
            else
            "🌙 " + self.t("dark_mode")
        )

        tk.Button(
            header,
            text=theme_text,
            command=self.toggle_theme,
            bg=self.colors["dark_blue"],
            fg="white",
            activebackground=self.colors["blue"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold")
        ).pack(
            side="right",
            padx=18
        )

        # Refresh button

        tk.Button(
            header,
            text="↻ " + self.t("refresh"),
            command=self.refresh_screen,
            bg=self.colors["blue"],
            fg="white",
            activebackground=self.colors["dark_blue"],
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            font=("Arial", 10, "bold")
        ).pack(side="right", padx=5)

        # Back button

        if show_back:

            tk.Button(
                header,
                text="← " + self.t("back"),
                command=self.show_home,
                bg=self.colors["red"],
                fg="white",
                activebackground=self.colors["dark_red"],
                activeforeground="white",
                relief="flat",
                bd=0,
                padx=15,
                pady=8,
                cursor="hand2",
                font=("Arial", 10, "bold")
            ).pack(
                side="right",
                padx=5
            )

        # Right red strip

        tk.Frame(
            header,
            bg=self.colors["red"],
            width=8
        ).pack(
            side="right",
            fill="y"
        )

    # ========================================================
    # BUTTON
    # ========================================================

    def make_button(
        self,
        parent,
        text,
        command,
        color=None,
        width=20
    ):

        if color is None:
            color = self.colors["blue"]

        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg="white",
            activebackground=self.colors["dark_blue"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            padx=12,
            pady=9,
            width=width
        )

    # ========================================================
    # FIELD LABEL
    # ========================================================

    def field_label(self, parent, text):

        tk.Label(
            parent,
            text=text,
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Arial", 10, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(8, 4)
        )

    # ========================================================
    # ENTRY
    # ========================================================

    def entry(self, parent, show=None):

        e = tk.Entry(
            parent,
            bg=self.colors["white"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="solid",
            bd=1,
            highlightthickness=0,
            font=("Arial", 10)
        )

        if show:
            e.configure(show=show)

        e.pack(
            fill="x",
            padx=20,
            pady=(0, 5),
            ipady=7
        )

        return e

    # ========================================================
    # COMBOBOX
    # ========================================================

    def combo(self, parent, values):

        box = ttk.Combobox(
            parent,
            values=values,
            state="readonly",
            font=("Arial", 10)
        )

        box.pack(
            fill="x",
            padx=20,
            pady=(0, 5),
            ipady=5
        )

        return box

    # ========================================================
    # HOME
    # ========================================================

    def show_home(self):

        self.current_screen = self.show_home

        self.clear_screen()

        self.create_header(
            self.t("app_title"),
            self.t("home_subtitle")
        )

        content = self.create_scrollable_frame()

        # ----------------------------------------------------
        # Language
        # ----------------------------------------------------

        language_frame = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        language_frame.pack(
            fill="x",
            padx=35,
            pady=15
        )

        tk.Label(
            language_frame,
            text=self.t("language") + ":",
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Arial", 10, "bold")
        ).pack(
            side="left"
        )

        language_box = ttk.Combobox(
            language_frame,
            values=["English", "Amharic"] if self.language == "en" else ["እንግሊዝኛ", "አማርኛ"],
            state="readonly",
            width=15
        )

        language_box.set(
            "English" if self.language == "en"
            else "አማርኛ"
        )

        language_box.pack(
            side="left",
            padx=10
        )

        language_box.bind(
            "<<ComboboxSelected>>",
            lambda e: self.change_language(
                "en" if language_box.get() == ("English" if self.language == "en" else "እንግሊዝኛ")
                else "am"
            )
        )

        # ----------------------------------------------------
        # Welcome
        # ----------------------------------------------------

        tk.Label(
            content,
            text=self.t("welcome"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 27, "bold")
        ).pack(
            pady=(10, 5)
        )

        tk.Label(
            content,
            text=self.t("home_description"),
            bg=self.colors["bg"],
            fg=self.colors["gray"],
            font=("Arial", 11)
        ).pack(
            pady=(0, 25)
        )

        # ----------------------------------------------------
        # Main buttons
        # ----------------------------------------------------

        cards = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        cards.pack(
            fill="x",
            padx=35
        )

        card_data = [
            (
                "👤",
                self.t("create_account"),
                self.t("create_account_desc"),
                self.register_user,
                self.colors["blue"]
            ),
            (
                "🔐",
                self.t("user_login"),
                self.t("login_desc"),
                self.user_login,
                self.colors["dark_blue"]
            ),
            (
                "🛡",
                self.t("administrator"),
                self.t("admin_desc"),
                self.admin_login,
                self.colors["red"]
            ),
            (
                "☎",
                self.t("emergency_contacts"),
                self.t("contacts_desc"),
                self.emergency_contacts,
                self.colors["orange"]
            )
        ]

        for i, data in enumerate(card_data):

            icon, title, description, command, color = data

            card = tk.Frame(
                cards,
                bg=self.colors["white"],
                bd=1,
                relief="solid",
                highlightbackground=self.colors["border"],
                highlightcolor=self.colors["border"],
                highlightthickness=2
            )

            tk.Frame(card, bg=color, height=5).pack(fill="x")

            card.grid(
                row=0,
                column=i,
                padx=8,
                pady=10,
                sticky="nsew"
            )

            cards.columnconfigure(
                i,
                weight=1
            )

            tk.Label(
                card,
                text=icon,
                bg=self.colors["white"],
                fg=color,
                font=("Arial", 28)
            ).pack(
                pady=(20, 5)
            )

            tk.Label(
                card,
                text=title,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 13, "bold")
            ).pack(
                pady=5
            )

            tk.Label(
                card,
                text=description,
                bg=self.colors["white"],
                fg=self.colors["gray"],
                font=("Arial", 9),
                wraplength=190,
                justify="center"
            ).pack(
                padx=10,
                pady=5
            )

            self.make_button(
                card,
                title,
                command,
                color,
                16
            ).pack(
                pady=(10, 20)
            )

        # ----------------------------------------------------
        # Emergency Types
        # IMPORTANT:
        # NO LOCATIONS ARE SHOWN HERE.
        # ----------------------------------------------------

        tk.Label(
            content,
            text=self.t("emergency_types"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 21, "bold")
        ).pack(
            pady=(35, 5)
        )

        tk.Label(
            content,
            text=self.t("emergency_select_desc"),
            bg=self.colors["bg"],
            fg=self.colors["gray"],
            font=("Arial", 10)
        ).pack(
            pady=(0, 15)
        )

        emergency_frame = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        emergency_frame.pack(
            fill="x",
            padx=30
        )

        for i, item in enumerate(self.emergency_types):

            row = i // 4
            col = i % 4

            emergency_frame.columnconfigure(
                col,
                weight=1
            )

            card = tk.Frame(
                emergency_frame,
                bg=self.colors["white"],
                bd=1,
                relief="solid",
                highlightbackground=self.colors["border"],
                highlightthickness=1
            )

            card.grid(
                row=row,
                column=col,
                padx=7,
                pady=7,
                sticky="nsew"
            )

            tk.Label(
                card,
                text=self.emergency_name(item),
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 11, "bold"),
                wraplength=220,
                justify="center"
            ).pack(
                padx=8,
                pady=(14, 8)
            )

            tk.Label(
                card,
                text=self.emergency_description(item),
                bg=self.colors["white"],
                fg=self.colors["gray"],
                font=("Arial", 8),
                wraplength=220,
                justify="center"
            ).pack(
                padx=10,
                pady=5
            )

            safety = tk.Label(
                card,
                text=(
                    "⚠ " +
                    self.t("safety_rule") +
                    "\n" +
                    self.emergency_safety(item)
                ),
                bg=self.colors["light_red"],
                fg=self.colors["dark_red"],
                font=("Arial", 8),
                wraplength=220,
                justify="left"
            )

            safety.pack(
                fill="x",
                padx=8,
                pady=(8, 12)
            )

        # ----------------------------------------------------
        # Footer
        # ----------------------------------------------------

        tk.Label(
            content,
            text=self.t("footer"),
            bg=self.colors["bg"],
            fg=self.colors["gray"],
            font=("Arial", 9)
        ).pack(
            pady=30
        )

    # ========================================================
    # CHANGE LANGUAGE
    # ========================================================

    def change_language(self, language):

        self.language = language
        self.root.title(self.t("app_title"))

        if self.current_screen:
            self.current_screen()

    # ========================================================
    # REGISTER USER
    # ========================================================

    def register_user(self):

        self.current_screen = self.register_user

        self.clear_screen()

        self.create_header(
            self.t("create_account"),
            self.t("create_account_desc"),
            True
        )

        content = self.create_scrollable_frame()

        form = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        form.pack(
            padx=150,
            pady=30,
            fill="x"
        )

        tk.Label(
            form,
            text=self.t("create_account"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
            font=("Arial", 22, "bold")
        ).pack(
            pady=(25, 10)
        )

        # ----------------------------------------------------
        # Full Name
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("full_name")
        )

        full_name = self.entry(form)

        # ----------------------------------------------------
        # Age
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("age")
        )

        age = self.entry(form)

        # ----------------------------------------------------
        # Gender
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("gender")
        )

        gender = self.combo(
            form,
            [
                self.t("male"),
                self.t("female"),
                self.t("other_gender")
            ]
        )

        # ----------------------------------------------------
        # Phone
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("phone")
        )

        phone = self.entry(form)

        # ----------------------------------------------------
        # Email
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("email")
        )

        email = self.entry(form)

        # ----------------------------------------------------
        # EXACT ADDRESS
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("location")
        )

        tk.Label(
            form,
            text=self.t("exact_location"),
            bg=self.colors["white"],
            fg=self.colors["gray"],
            font=("Arial", 9),
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 4)
        )

        address = self.entry(form)

        # ----------------------------------------------------
        # Username
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("username")
        )

        username = self.entry(form)

        # ----------------------------------------------------
        # Password
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("password")
        )

        password = self.entry(
            form,
            "●"
        )

        # ----------------------------------------------------
        # Confirm Password
        # ----------------------------------------------------

        self.field_label(
            form,
            self.t("confirm_password")
        )

        confirm_password = self.entry(
            form,
            "●"
        )

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        def save_user():

            values = [
                full_name.get().strip(),
                age.get().strip(),
                gender.get().strip(),
                phone.get().strip(),
                email.get().strip(),
                address.get().strip(),
                username.get().strip(),
                password.get(),
                confirm_password.get()
            ]

            if not all(values):

                messagebox.showwarning(
                    self.t("required"),
                    self.t("required")
                )

                return

            # Validate all user-entered information.
            if not re.fullmatch(r"[A-Za-z\u1200-\u137F][A-Za-z\u1200-\u137F .\'-]{1,79}", full_name.get().strip()):
                self.invalid()
                return

            if not re.fullmatch(r"\d{1,3}", age.get().strip()):
                self.invalid()
                return

            age_value = int(age.get().strip())
            if age_value < 1 or age_value > 120:
                self.invalid()
                return

            if not gender.get().strip():
                self.invalid()
                return

            if not re.fullmatch(r"\+?[0-9][0-9 -]{7,19}", phone.get().strip()):
                self.invalid()
                return

            if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.get().strip()):
                self.invalid()
                return

            if not re.fullmatch(r"(?=.*[A-Za-z\u1200-\u137F])[A-Za-z\u1200-\u137F0-9 .,'/#()\-]{3,200}", address.get().strip()):
                self.invalid()
                return

            if not re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username.get().strip()):
                self.invalid()
                return

            if len(password.get()) < 4 or password.get() != confirm_password.get():
                self.invalid()
                return

            conn = get_db()

            try:

                conn.execute("""
                    INSERT INTO users
                    (
                        full_name,
                        age,
                        gender,
                        phone,
                        email,
                        address,
                        username,
                        password,
                        created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    full_name.get().strip(),
                    age_value,
                    gender.get().strip(),
                    phone.get().strip(),
                    email.get().strip(),
                    address.get().strip(),
                    username.get().strip(),
                    hash_password(password.get()),
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                ))

                conn.commit()

                messagebox.showinfo(
                    self.t("account_created"),
                    self.t("account_created")
                )

                conn.close()

                self.user_login()

            except sqlite3.IntegrityError:

                conn.close()

                messagebox.showerror(
                    self.t("error"),
                    self.t("username_exists")
                )

            except Exception as e:

                conn.close()

                messagebox.showerror(
                    self.t("error"),
                    str(e)
                )

        button_frame = tk.Frame(
            form,
            bg=self.colors["white"]
        )

        button_frame.pack(
            pady=25
        )

        self.make_button(
            button_frame,
            self.t("register"),
            save_user,
            self.colors["blue"],
            18
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            button_frame,
            self.t("back"),
            self.show_home,
            self.colors["gray"],
            18
        ).pack(
            side="left",
            padx=5
        )

    # ========================================================
    # USER LOGIN
    # ========================================================

    def user_login(self):

        self.current_screen = self.user_login

        self.clear_screen()

        self.create_header(
            self.t("user_login"),
            self.t("login_subtitle"),
            True
        )

        content = self.create_scrollable_frame()

        form = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        form.pack(
            padx=300,
            pady=80,
            fill="x"
        )

        tk.Label(
            form,
            text="🔐",
            bg=self.colors["white"],
            fg=self.colors["blue"],
            font=("Arial", 35)
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            form,
            text=self.t("user_login"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
            font=("Arial", 22, "bold")
        ).pack(
            pady=(0, 20)
        )

        self.field_label(
            form,
            self.t("username")
        )

        username = self.entry(form)

        self.field_label(
            form,
            self.t("password")
        )

        password = self.entry(
            form,
            "●"
        )

        def login():

            conn = get_db()

            user = conn.execute("""
                SELECT * FROM users
                WHERE username = ?
                AND password = ?
            """, (
                username.get().strip(),
                hash_password(password.get())
            )).fetchone()

            conn.close()

            if user:

                self.current_user = dict(user)

                self.user_dashboard()

            else:

                messagebox.showerror(
                    self.t("login_failed"),
                    self.t("login_failed")
                )

        self.make_button(
            form,
            self.t("login"),
            login,
            self.colors["blue"],
            20
        ).pack(
            pady=(20, 8)
        )

        self.make_button(
            form,
            self.t("create_account"),
            self.register_user,
            self.colors["green"],
            20
        ).pack(
            pady=5
        )

        self.make_button(
            form,
            self.t("back"),
            self.show_home,
            self.colors["gray"],
            20
        ).pack(
            pady=(5, 25)
        )

    # ========================================================
    # USER SIDEBAR
    # ========================================================

    def user_sidebar(self, parent):

        sidebar = tk.Frame(
            parent,
            bg=self.colors["dark_blue"],
            width=230
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        name = ""

        if self.current_user:
            name = self.current_user.get(
                "full_name",
                ""
            )

        tk.Label(
            sidebar,
            text="👤",
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 35)
        ).pack(
            pady=(30, 5)
        )

        tk.Label(
            sidebar,
            text=name,
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 11, "bold"),
            wraplength=190
        ).pack(
            padx=10,
            pady=(0, 25)
        )

        buttons = [
            (
                self.t("dashboard"),
                self.user_dashboard,
                self.colors["blue"]
            ),
            (
                self.t("report_emergency"),
                self.report_emergency,
                self.colors["red"]
            ),
            (
                self.t("my_reports"),
                self.my_reports,
                self.colors["blue"]
            ),
            (
                self.t("my_profile"),
                self.my_profile,
                self.colors["blue"]
            ),
            (
                self.t("emergency_contacts"),
                self.emergency_contacts,
                self.colors["orange"]
            )
        ]

        for text, command, color in buttons:

            tk.Button(
                sidebar,
                text=text,
                command=command,
                bg=color,
                fg="white",
                activebackground=self.colors["dark_red"]
                if color == self.colors["red"]
                else self.colors["dark_blue"],
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Arial", 9, "bold"),
                anchor="w",
                padx=20,
                pady=10
            ).pack(
                fill="x",
                padx=12,
                pady=3
            )

        tk.Frame(
            sidebar,
            bg=self.colors["dark_blue"]
        ).pack(
            fill="both",
            expand=True
        )

        tk.Button(
            sidebar,
            text="🚪 " + self.t("logout"),
            command=self.logout,
            bg=self.colors["red"],
            fg="white",
            activebackground=self.colors["dark_red"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            pady=10
        ).pack(
            fill="x",
            padx=12,
            pady=20
        )

    # ========================================================
    # USER DASHBOARD
    # ========================================================

    def user_dashboard(self):

        self.current_screen = self.user_dashboard

        self.clear_screen()

        top = tk.Frame(
            self.root,
            bg=self.colors["dark_blue"],
            height=75
        )

        top.pack(
            fill="x"
        )

        top.pack_propagate(False)

        tk.Label(
            top,
            text=self.t("dashboard"),
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 20, "bold")
        ).pack(
            side="left",
            padx=25
        )

        theme_text = (
            "☀ " + self.t("light_mode")
            if self.dark_mode
            else
            "🌙 " + self.t("dark_mode")
        )

        tk.Button(
            top,
            text=theme_text,
            command=self.toggle_theme,
            bg=self.colors["dark_blue"],
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 9, "bold")
        ).pack(
            side="right",
            padx=20
        )
        tk.Button(
            top,
            text="↻ " + self.t("refresh"),
            command=self.refresh_screen,
            bg=self.colors["blue"],
            fg="white",
            activebackground=self.colors["dark_blue"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=6
        ).pack(side="right", padx=5)


        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.user_sidebar(main)

        content = tk.Frame(
            main,
            bg=self.colors["bg"]
        )

        content.pack(
            side="left",
            fill="both",
            expand=True
        )

        tk.Label(
            content,
            text=self.t("welcome") + ", " +
                 self.current_user["full_name"],
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 5)
        )

        tk.Label(
            content,
            text=self.t("manage_info_desc"),
            bg=self.colors["bg"],
            fg=self.colors["gray"],
            font=("Arial", 10)
        ).pack(
            anchor="w",
            padx=30,
            pady=(0, 25)
        )

        conn = get_db()

        total = conn.execute("""
            SELECT COUNT(*) AS total
            FROM emergency_reports
            WHERE user_id = ?
        """, (
            self.current_user["id"],
        )).fetchone()["total"]

        pending = conn.execute("""
            SELECT COUNT(*) AS total
            FROM emergency_reports
            WHERE user_id = ?
            AND status = 'Pending'
        """, (
            self.current_user["id"],
        )).fetchone()["total"]

        resolved = conn.execute("""
            SELECT COUNT(*) AS total
            FROM emergency_reports
            WHERE user_id = ?
            AND status = 'Resolved'
        """, (
            self.current_user["id"],
        )).fetchone()["total"]

        conn.close()

        stats = [
            (
                self.t("total_reports"),
                total,
                self.colors["blue"]
            ),
            (
                self.t("pending_reports"),
                pending,
                self.colors["orange"]
            ),
            (
                self.t("resolved_reports"),
                resolved,
                self.colors["green"]
            )
        ]

        stat_frame = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        stat_frame.pack(
            fill="x",
            padx=25
        )

        for i, (title, number, color) in enumerate(stats):

            stat_frame.columnconfigure(
                i,
                weight=1
            )

            card = tk.Frame(
                stat_frame,
                bg=self.colors["white"],
                bd=1,
                relief="solid"
            )

            card.grid(
                row=0,
                column=i,
                padx=7,
                pady=7,
                sticky="nsew"
            )

            tk.Label(
                card,
                text=str(number),
                bg=self.colors["white"],
                fg=color,
                font=("Arial", 28, "bold")
            ).pack(
                pady=(20, 3)
            )

            tk.Label(
                card,
                text=title,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 10, "bold")
            ).pack(
                pady=(0, 20)
            )

        # Quick report

        report_card = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        report_card.pack(
            fill="x",
            padx=30,
            pady=30
        )

        tk.Label(
            report_card,
            text=self.t("report_emergency"),
            bg=self.colors["white"],
            fg=self.colors["red"],
            font=("Arial", 17, "bold")
        ).pack(
            pady=(20, 5)
        )

        tk.Label(
            report_card,
            text=self.t("report_warning"),
            bg=self.colors["white"],
            fg=self.colors["gray"],
            font=("Arial", 10)
        ).pack(
            pady=5
        )

        self.make_button(
            report_card,
            "🚨 " + self.t("report_emergency"),
            self.report_emergency,
            self.colors["red"],
            25
        ).pack(
            pady=20
        )

    # ========================================================
    # REPORT EMERGENCY
    # ========================================================

    def report_emergency(self):

        if not self.current_user:
            self.user_login()
            return

        self.current_screen = self.report_emergency

        self.clear_screen()

        self.create_header(
            self.t("report_emergency"),
            self.t("report_subtitle"),
            True
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.user_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        form = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        form.pack(
            padx=50,
            pady=30,
            fill="x"
        )

        tk.Label(
            form,
            text="🚨 " + self.t("report_emergency"),
            bg=self.colors["white"],
            fg=self.colors["red"],
            font=("Arial", 22, "bold")
        ).pack(
            pady=(25, 15)
        )

        # Emergency type

        self.field_label(
            form,
            self.t("emergency_type")
        )

        emergency_type = self.combo(
            form,
            self.get_emergency_names()
        )

        # Location

        self.field_label(
            form,
            self.t("location")
        )

        tk.Label(
            form,
            text=self.t("exact_location"),
            bg=self.colors["white"],
            fg=self.colors["gray"],
            font=("Arial", 9),
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(0, 4)
        )

        location = self.entry(form)

        # Description

        self.field_label(
            form,
            self.t("description")
        )

        description = tk.Text(
            form,
            height=6,
            bg=self.colors["white"],
            fg=self.colors["text"],
            insertbackground=self.colors["text"],
            relief="solid",
            bd=1,
            font=("Arial", 10)
        )

        description.pack(
            fill="x",
            padx=20,
            pady=(0, 5)
        )

        # People affected

        self.field_label(
            form,
            self.t("people_affected")
        )

        people = self.entry(form)

        # Priority

        self.field_label(
            form,
            self.t("priority")
        )

        priority = self.combo(
            form,
            [
                self.t("high"),
                self.t("medium"),
                self.t("low")
            ]
        )

        priority.set(
            self.t("medium")
        )

        # ----------------------------------------------------
        # SAFETY INFORMATION
        # ----------------------------------------------------

        info_frame = tk.Frame(
            form,
            bg=self.colors["light_red"]
        )

        info_frame.pack(
            fill="x",
            padx=20,
            pady=20
        )

        safety_label = tk.Label(
            info_frame,
            text="",
            bg=self.colors["light_red"],
            fg=self.colors["dark_red"],
            font=("Arial", 9),
            wraplength=800,
            justify="left"
        )

        safety_label.pack(
            padx=15,
            pady=12
        )

        def update_safety(event=None):

            selected = emergency_type.get()

            for item in self.emergency_types:

                if (
                    selected == item["en"]
                    or
                    selected == item["am"]
                ):

                    safety_label.config(
                        text=(
                            "⚠ " +
                            self.t("safety_rule") +
                            ": " +
                            self.emergency_safety(item)
                        )
                    )

                    break

        emergency_type.bind(
            "<<ComboboxSelected>>",
            update_safety
        )

        # ----------------------------------------------------
        # SUBMIT
        # ----------------------------------------------------

        def submit_report():

            if not emergency_type.get().strip() or not location.get().strip():
                self.invalid()
                return

            if not re.fullmatch(r"(?=.*[A-Za-z\u1200-\u137F])[A-Za-z\u1200-\u137F0-9 .,'/#()\-]{3,200}", location.get().strip()):
                self.invalid()
                return

            desc = description.get(
                "1.0",
                "end"
            ).strip()

            if len(desc) < 3 or not re.search(r"[A-Za-z0-9\u1200-\u137F]", desc):
                self.invalid()
                return

            try:
                affected = int(people.get().strip())
                if affected < 1 or affected > 1000000:
                    raise ValueError
            except (ValueError, TypeError):
                self.invalid()
                return

            db_type = self.get_emergency_db_value(
                emergency_type.get()
            )

            priority_db = priority.get()

            if self.language == "am":

                priority_map = {
                    "ከፍተኛ": "High",
                    "መካከለኛ": "Medium",
                    "ዝቅተኛ": "Low"
                }

                priority_db = priority_map.get(
                    priority_db,
                    "Medium"
                )

            conn = get_db()

            conn.execute("""
                INSERT INTO emergency_reports
                (
                    user_id,
                    emergency_type,
                    location,
                    description,
                    people_affected,
                    priority,
                    status,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.current_user["id"],
                db_type,
                location.get().strip(),
                desc,
                affected,
                priority_db,
                "Pending",
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            ))

            conn.commit()
            conn.close()

            messagebox.showinfo(
                self.t("report_created"),
                self.t("report_created")
            )

            self.user_dashboard()

        self.make_button(
            form,
            "🚨 " + self.t("submit"),
            submit_report,
            self.colors["red"],
            25
        ).pack(
            pady=(5, 25)
        )

    # ========================================================
    # SCROLLABLE FRAME FOR PARENT
    # ========================================================

    def create_scrollable_frame_for_parent(self, parent):

        outer = tk.Frame(
            parent,
            bg=self.colors["bg"]
        )

        outer.pack(
            side="left",
            fill="both",
            expand=True
        )

        canvas = tk.Canvas(
            outer,
            bg=self.colors["bg"],
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            outer,
            orient="vertical",
            command=canvas.yview
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        content = tk.Frame(
            canvas,
            bg=self.colors["bg"]
        )

        window_id = canvas.create_window(
            (0, 0),
            window=content,
            anchor="nw"
        )

        content.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfig(
                window_id,
                width=e.width
            )
        )

        return content

    # ========================================================
    # MY REPORTS
    # ========================================================

    def my_reports(self):

        self.current_screen = self.my_reports

        self.clear_screen()

        self.create_header(
            self.t("my_reports"),
            self.t("reports_subtitle"),
            True
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.user_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        tk.Label(
            content,
            text=self.t("my_reports"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=25
        )

        conn = get_db()

        reports = conn.execute("""
            SELECT *
            FROM emergency_reports
            WHERE user_id = ?
            ORDER BY id DESC
        """, (
            self.current_user["id"],
        )).fetchall()

        conn.close()

        if not reports:

            tk.Label(
                content,
                text=self.t("no_reports"),
                bg=self.colors["bg"],
                fg=self.colors["gray"],
                font=("Arial", 12)
            ).pack(
                pady=50
            )

            return

        table_frame = tk.Frame(
            content,
            bg=self.colors["white"]
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=10
        )

        columns = (
            "id",
            "type",
            "location",
            "priority",
            "status",
            "date"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": self.t("id"),
            "type": self.t("emergency_type"),
            "location": self.t("location"),
            "priority": self.t("priority"),
            "status": self.t("status"),
            "date": self.t("date")
        }

        widths = {
            "id": 60,
            "type": 200,
            "location": 150,
            "priority": 100,
            "status": 120,
            "date": 160
        }

        for column in columns:

            tree.heading(
                column,
                text=headings[column]
            )

            tree.column(
                column,
                width=widths[column],
                anchor="center"
            )

        for report in reports:

            tree.insert(
                "",
                "end",
                values=(
                    report["id"],
                    self.get_emergency_display_name(
                        report["emergency_type"]
                    ),
                    self.display_location(report["location"]),
                    self.display_priority(report["priority"]),
                    self.display_status(report["status"]),
                    report["created_at"]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        def details():

            selected = tree.selection()

            if not selected:
                return

            values = tree.item(
                selected[0],
                "values"
            )

            report_id = values[0]

            self.view_report(
                report_id,
                False
            )

        self.make_button(
            content,
            self.t("view_details"),
            details,
            self.colors["blue"],
            20
        ).pack(
            pady=20
        )

    # ========================================================
    # VIEW REPORT
    # ========================================================

    def view_report(
        self,
        report_id,
        admin=False
    ):

        conn = get_db()

        report = conn.execute("""
            SELECT emergency_reports.*, users.full_name
            FROM emergency_reports
            LEFT JOIN users
            ON emergency_reports.user_id = users.id
            WHERE emergency_reports.id = ?
        """, (
            report_id,
        )).fetchone()

        conn.close()

        if not report:
            return

        window = tk.Toplevel(
            self.root
        )

        window.title(
            self.t("details")
        )

        window.geometry(
            "650x600"
        )

        window.configure(
            bg=self.colors["bg"]
        )

        tk.Label(
            window,
            text=self.t("details"),
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 18, "bold")
        ).pack(
            fill="x",
            pady=15
        )

        frame = tk.Frame(
            window,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        data = [
            (
                self.t("id"),
                report["id"]
            ),
            (
                self.t("user"),
                report["full_name"]
            ),
            (
                self.t("emergency_type"),
                self.get_emergency_display_name(
                    report["emergency_type"]
                )
            ),
            (
                self.t("location"),
                report["location"]
            ),
            (
                self.t("people_affected"),
                report["people_affected"]
            ),
            (
                self.t("priority"),
                report["priority"]
            ),
            (
                self.t("status"),
                report["status"]
            ),
            (
                "Created",
                report["created_at"]
            )
        ]

        for label, value in data:

            row = tk.Frame(
                frame,
                bg=self.colors["white"]
            )

            row.pack(
                fill="x",
                padx=20,
                pady=7
            )

            tk.Label(
                row,
                text=str(label) + ":",
                bg=self.colors["white"],
                fg=self.colors["dark_blue"],
                font=("Arial", 10, "bold"),
                width=20,
                anchor="w"
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                text=str(value),
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 10),
                anchor="w",
                wraplength=350,
                justify="left"
            ).pack(
                side="left",
                fill="x",
                expand=True
            )

        tk.Label(
            frame,
            text=self.t("description"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
            font=("Arial", 10, "bold"),
            anchor="w"
        ).pack(
            fill="x",
            padx=20,
            pady=(15, 5)
        )

        tk.Label(
            frame,
            text=report["description"],
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Arial", 10),
            wraplength=500,
            justify="left",
            anchor="w"
        ).pack(
            fill="x",
            padx=20
        )

        self.make_button(
            frame,
            self.t("close"),
            window.destroy,
            self.colors["gray"],
            15
        ).pack(
            pady=20
        )

    # ========================================================
    # PROFILE
    # ========================================================

    def my_profile(self):

        self.current_screen = self.my_profile

        self.clear_screen()

        self.create_header(
            self.t("my_profile"),
            self.t("profile_subtitle"),
            True
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.user_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        card = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        card.pack(
            padx=80,
            pady=40,
            fill="x"
        )

        tk.Label(
            card,
            text="👤",
            bg=self.colors["white"],
            fg=self.colors["blue"],
            font=("Arial", 35)
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            card,
            text=self.current_user["full_name"],
            bg=self.colors["white"],
            fg=self.colors["text"],
            font=("Arial", 20, "bold")
        ).pack(
            pady=(0, 20)
        )

        data = [
            (
                self.t("full_name"),
                self.current_user["full_name"]
            ),
            (
                self.t("age"),
                self.current_user["age"]
            ),
            (
                self.t("gender"),
                self.current_user["gender"]
            ),
            (
                self.t("phone"),
                self.current_user["phone"]
            ),
            (
                self.t("email"),
                self.current_user["email"]
            ),
            (
                self.t("address"),
                self.current_user["address"]
            ),
            (
                self.t("emergency_type"),
                self.get_emergency_display_name(
                    self.current_user.get(
                        "emergency_type",
                        ""
                    )
                )
            ),
            (
                self.t("emergency_contact"),
                self.current_user["emergency_contact"]
            ),
            (
                self.t("username"),
                self.current_user["username"]
            )
        ]

        for label, value in data:

            row = tk.Frame(
                card,
                bg=self.colors["white"]
            )

            row.pack(
                fill="x",
                padx=40,
                pady=7
            )

            tk.Label(
                row,
                text=str(label),
                bg=self.colors["white"],
                fg=self.colors["dark_blue"],
                font=("Arial", 10, "bold"),
                width=22,
                anchor="w"
            ).pack(
                side="left"
            )

            tk.Label(
                row,
                text=str(value or ""),
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 10),
                anchor="w"
            ).pack(
                side="left"
            )

        self.make_button(
            card,
            self.t("back"),
            self.user_dashboard,
            self.colors["gray"],
            18
        ).pack(
            pady=25
        )

    # ========================================================
    # ADMIN LOGIN
    # ========================================================

    def admin_login(self):

        self.current_screen = self.admin_login

        self.clear_screen()

        self.create_header(
            self.t("admin_login"),
            self.t("admin_access"),
            True
        )

        content = self.create_scrollable_frame()

        form = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        form.pack(
            padx=300,
            pady=80,
            fill="x"
        )

        tk.Label(
            form,
            text="🛡",
            bg=self.colors["white"],
            fg=self.colors["red"],
            font=("Arial", 38)
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            form,
            text=self.t("admin_login"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
            font=("Arial", 22, "bold")
        ).pack(
            pady=(0, 20)
        )

        self.field_label(
            form,
            self.t("username")
        )

        username = self.entry(form)

        self.field_label(
            form,
            self.t("password")
        )

        password = self.entry(
            form,
            "●"
        )

        def login():

            conn = get_db()

            admin = conn.execute("""
                SELECT *
                FROM admins
                WHERE username = ?
                AND password = ?
            """, (
                username.get().strip(),
                hash_password(password.get())
            )).fetchone()

            conn.close()

            if admin:

                self.current_admin = dict(admin)

                self.admin_dashboard()

            else:

                messagebox.showerror(
                    self.t("login_failed"),
                    self.t("login_failed")
                )

        self.make_button(
            form,
            self.t("login"),
            login,
            self.colors["red"],
            20
        ).pack(
            pady=20
        )

        self.make_button(
            form,
            self.t("back"),
            self.show_home,
            self.colors["gray"],
            20
        ).pack(
            pady=(0, 25)
        )

    # ========================================================
    # ADMIN SIDEBAR
    # ========================================================

    def admin_sidebar(self, parent):

        sidebar = tk.Frame(
            parent,
            bg=self.colors["dark_blue"],
            width=240
        )

        sidebar.pack(
            side="left",
            fill="y"
        )

        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="🛡",
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 38)
        ).pack(
            pady=(25, 5)
        )

        tk.Label(
            sidebar,
            text=self.t("admin"),
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 13, "bold")
        ).pack(
            pady=(0, 25)
        )

        buttons = [
            (
                self.t("dashboard"),
                self.admin_dashboard,
                self.colors["blue"]
            ),
            (
                self.t("manage_users"),
                self.manage_users,
                self.colors["blue"]
            ),
            (
                self.t("manage_reports"),
                self.manage_reports,
                self.colors["blue"]
            ),
            (
                self.t("manage_contacts"),
                self.manage_contacts,
                self.colors["orange"]
            ),
            (
                self.t("emergency_contacts"),
                self.emergency_contacts,
                self.colors["orange"]
            ),
            (
                self.t("report_emergency"),
                self.report_emergency,
                self.colors["red"]
            )
        ]

        for text, command, color in buttons:

            tk.Button(
                sidebar,
                text=text,
                command=command,
                bg=color,
                fg="white",
                activebackground=self.colors["dark_blue"],
                activeforeground="white",
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Arial", 9, "bold"),
                anchor="w",
                padx=18,
                pady=9
            ).pack(
                fill="x",
                padx=10,
                pady=3
            )

        tk.Frame(
            sidebar,
            bg=self.colors["dark_blue"]
        ).pack(
            fill="both",
            expand=True
        )

        tk.Button(
            sidebar,
            text="🚪 " + self.t("logout"),
            command=self.logout,
            bg=self.colors["red"],
            fg="white",
            activebackground=self.colors["dark_red"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 10, "bold"),
            pady=10
        ).pack(
            fill="x",
            padx=10,
            pady=20
        )

    # ========================================================
    # ADMIN DASHBOARD
    # ========================================================

    def admin_dashboard(self):

        self.current_screen = self.admin_dashboard

        self.clear_screen()

        top = tk.Frame(
            self.root,
            bg=self.colors["dark_blue"],
            height=75
        )

        top.pack(
            fill="x"
        )

        top.pack_propagate(False)

        tk.Label(
            top,
            text=self.t("admin_dashboard"),
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 20, "bold")
        ).pack(
            side="left",
            padx=25
        )

        theme_text = (
            "☀ " + self.t("light_mode")
            if self.dark_mode
            else
            "🌙 " + self.t("dark_mode")
        )

        tk.Button(
            top,
            text=theme_text,
            command=self.toggle_theme,
            bg=self.colors["dark_blue"],
            fg="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 9, "bold")
        ).pack(
            side="right",
            padx=20
        )
        tk.Button(
            top,
            text="↻ " + self.t("refresh"),
            command=self.refresh_screen,
            bg=self.colors["blue"],
            fg="white",
            activebackground=self.colors["dark_blue"],
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
            font=("Arial", 9, "bold"),
            padx=10,
            pady=6
        ).pack(side="right", padx=5)


        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.admin_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        tk.Label(
            content,
            text=self.t("welcome") + ", " + self.t("administrator"),
            bg=self.colors["bg"],
            fg=self.colors["text"],
            font=("Arial", 22, "bold")
        ).pack(
            anchor="w",
            padx=30,
            pady=(30, 25)
        )

        conn = get_db()

        total_users = conn.execute(
            "SELECT COUNT(*) AS total FROM users"
        ).fetchone()["total"]

        total_reports = conn.execute(
            "SELECT COUNT(*) AS total FROM emergency_reports"
        ).fetchone()["total"]

        pending = conn.execute("""
            SELECT COUNT(*) AS total
            FROM emergency_reports
            WHERE status = 'Pending'
        """).fetchone()["total"]

        resolved = conn.execute("""
            SELECT COUNT(*) AS total
            FROM emergency_reports
            WHERE status = 'Resolved'
        """).fetchone()["total"]

        conn.close()

        stats = [
            (
                self.t("total_users"),
                total_users,
                self.colors["blue"]
            ),
            (
                self.t("total_reports"),
                total_reports,
                self.colors["red"]
            ),
            (
                self.t("pending_reports"),
                pending,
                self.colors["orange"]
            ),
            (
                self.t("resolved_reports"),
                resolved,
                self.colors["green"]
            )
        ]

        frame = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        frame.pack(
            fill="x",
            padx=25
        )

        for i, (title, number, color) in enumerate(stats):

            frame.columnconfigure(
                i,
                weight=1
            )

            card = tk.Frame(
                frame,
                bg=self.colors["white"],
                bd=1,
                relief="solid"
            )

            card.grid(
                row=0,
                column=i,
                padx=6,
                pady=6,
                sticky="nsew"
            )

            tk.Label(
                card,
                text=str(number),
                bg=self.colors["white"],
                fg=color,
                font=("Arial", 28, "bold")
            ).pack(
                pady=(20, 3)
            )

            tk.Label(
                card,
                text=title,
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 9, "bold")
            ).pack(
                pady=(0, 20)
            )

        quick = tk.Frame(
            content,
            bg=self.colors["white"],
            bd=1,
            relief="solid"
        )

        quick.pack(
            fill="x",
            padx=30,
            pady=30
        )

        tk.Label(
            quick,
            text=self.t("quick_actions"),
            bg=self.colors["white"],
            fg=self.colors["dark_blue"],
            font=("Arial", 17, "bold")
        ).pack(
            pady=(20, 15)
        )

        buttons = tk.Frame(
            quick,
            bg=self.colors["white"]
        )

        buttons.pack(
            pady=(0, 20)
        )

        self.make_button(
            buttons,
            self.t("manage_users"),
            self.manage_users,
            self.colors["blue"],
            18
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            buttons,
            self.t("manage_reports"),
            self.manage_reports,
            self.colors["red"],
            18
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            buttons,
            self.t("manage_contacts"),
            self.manage_contacts,
            self.colors["orange"],
            18
        ).pack(
            side="left",
            padx=5
        )

    # ========================================================
    # MANAGE USERS
    # ========================================================

    def manage_users(self):

        self.current_screen = self.manage_users

        self.clear_screen()

        self.create_header(
            self.t("manage_users"),
            self.t("users_subtitle")
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.admin_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        tk.Label(
            content,
            text=self.t("manage_users"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 21, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=20
        )

        table_frame = tk.Frame(
            content,
            bg=self.colors["white"]
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "id",
            "name",
            "username",
            "phone",
            "address",
            "emergency"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": self.t("id"),
            "name": self.t("full_name"),
            "username": self.t("username"),
            "phone": self.t("phone"),
            "address": self.t("address"),
            "emergency": self.t("emergency_type")
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=140,
                anchor="center"
            )

        conn = get_db()

        users = conn.execute("""
            SELECT *
            FROM users
            ORDER BY id DESC
        """).fetchall()

        conn.close()

        for user in users:

            tree.insert(
                "",
                "end",
                values=(
                    user["id"],
                    user["full_name"],
                    user["username"],
                    user["phone"],
                    self.display_location(user["address"]),
                    self.get_emergency_display_name(
                        user["emergency_type"] or ""
                    )
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        def delete_user():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    self.t("warning"),
                    self.t("select_user")
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            user_id = values[0]

            if not messagebox.askyesno(
                self.t("confirm"),
                self.t("confirm_delete")
            ):
                return

            conn = get_db()

            conn.execute(
                "DELETE FROM users WHERE id = ?",
                (user_id,)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                self.t("success"),
                self.t("user_deleted")
            )

            self.manage_users()

        self.make_button(
            content,
            self.t("delete"),
            delete_user,
            self.colors["red"],
            18
        ).pack(
            pady=20
        )

    # ========================================================
    # MANAGE REPORTS
    # ========================================================

    def manage_reports(self):

        self.current_screen = self.manage_reports

        self.clear_screen()

        self.create_header(
            self.t("manage_reports"),
            self.t("reports_manage_subtitle")
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.admin_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        tk.Label(
            content,
            text=self.t("manage_reports"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 21, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=20
        )

        table_frame = tk.Frame(
            content,
            bg=self.colors["white"]
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        columns = (
            "id",
            "user",
            "type",
            "location",
            "priority",
            "status",
            "date"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        headings = {
            "id": self.t("id"),
            "user": self.t("user"),
            "type": self.t("emergency_type"),
            "location": self.t("location"),
            "priority": self.t("priority"),
            "status": self.t("status"),
            "date": self.t("date")
        }

        widths = {
            "id": 50,
            "user": 150,
            "type": 180,
            "location": 120,
            "priority": 100,
            "status": 120,
            "date": 150
        }

        for col in columns:

            tree.heading(
                col,
                text=headings[col]
            )

            tree.column(
                col,
                width=widths[col],
                anchor="center"
            )

        conn = get_db()

        reports = conn.execute("""
            SELECT emergency_reports.*,
                   users.full_name
            FROM emergency_reports
            LEFT JOIN users
            ON emergency_reports.user_id = users.id
            ORDER BY emergency_reports.id DESC
        """).fetchall()

        conn.close()

        for report in reports:

            tree.insert(
                "",
                "end",
                values=(
                    report["id"],
                    report["full_name"],
                    self.get_emergency_display_name(
                        report["emergency_type"]
                    ),
                    self.display_location(report["location"]),
                    self.display_priority(report["priority"]),
                    self.display_status(report["status"]),
                    report["created_at"]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        buttons.pack(
            pady=20
        )

        def selected_report():

            selected = tree.selection()

            if not selected:

                messagebox.showwarning(
                    self.t("warning"),
                    self.t("select_report")
                )

                return None

            values = tree.item(
                selected[0],
                "values"
            )

            return values[0]

        def view():

            report_id = selected_report()

            if report_id:
                self.view_report(
                    report_id,
                    True
                )

        def update_status():

            report_id = selected_report()

            if not report_id:
                return

            window = tk.Toplevel(
                self.root
            )

            window.title(
                self.t("status")
            )

            window.geometry(
                "350x220"
            )

            window.configure(
                bg=self.colors["bg"]
            )

            tk.Label(
                window,
                text=self.t("status"),
                bg=self.colors["bg"],
                fg=self.colors["text"],
                font=("Arial", 14, "bold")
            ).pack(
                pady=20
            )

            status = ttk.Combobox(
                window,
                values=(
                    ["Pending", "In Progress", "Resolved"]
                    if self.language == "en"
                    else ["በመጠባበቅ ላይ", "በሂደት ላይ", "ተፈቷል"]
                ),
                state="readonly"
            )

            status.pack(
                padx=30,
                fill="x"
            )

            status.set(
                "Pending" if self.language == "en" else "በመጠባበቅ ላይ"
            )

            def save():

                conn = get_db()

                conn.execute("""
                    UPDATE emergency_reports
                    SET status = ?
                    WHERE id = ?
                """, (
                    {"በመጠባበቅ ላይ": "Pending", "በሂደት ላይ": "In Progress", "ተፈቷል": "Resolved"}.get(status.get(), status.get()),
                    report_id
                ))

                conn.commit()
                conn.close()

                window.destroy()

                self.manage_reports()

            self.make_button(
                window,
                self.t("save"),
                save,
                self.colors["blue"],
                15
            ).pack(
                pady=20
            )

        def delete():

            report_id = selected_report()

            if not report_id:
                return

            if not messagebox.askyesno(
                self.t("confirm"),
                self.t("confirm_delete")
            ):
                return

            conn = get_db()

            conn.execute(
                "DELETE FROM emergency_reports WHERE id = ?",
                (report_id,)
            )

            conn.commit()
            conn.close()

            messagebox.showinfo(
                self.t("success"),
                self.t("report_deleted")
            )

            self.manage_reports()

        self.make_button(
            buttons,
            self.t("view_details"),
            view,
            self.colors["blue"],
            16
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            buttons,
            self.t("status"),
            update_status,
            self.colors["orange"],
            16
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            buttons,
            self.t("delete"),
            delete,
            self.colors["red"],
            16
        ).pack(
            side="left",
            padx=5
        )

    # ========================================================
    # EMERGENCY CONTACTS
    # ========================================================

    def emergency_contacts(self):

        self.current_screen = self.emergency_contacts

        self.clear_screen()

        self.create_header(
            self.t("emergency_contacts"),
            self.t("contacts_desc"),
            True
        )

        content = self.create_scrollable_frame()

        tk.Label(
            content,
            text=self.t("emergency_contacts"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 23, "bold")
        ).pack(
            pady=(30, 5)
        )

        tk.Label(
            content,
            text=self.t("contacts_subtitle"),
            bg=self.colors["bg"],
            fg=self.colors["gray"],
            font=("Arial", 10)
        ).pack(
            pady=(0, 25)
        )

        conn = get_db()

        contacts = conn.execute("""
            SELECT *
            FROM emergency_contacts
            ORDER BY id
        """).fetchall()

        conn.close()

        frame = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        frame.pack(
            fill="x",
            padx=60
        )

        for i, contact in enumerate(contacts):

            row = i // 2
            col = i % 2

            frame.columnconfigure(
                col,
                weight=1
            )

            card = tk.Frame(
                frame,
                bg=self.colors["white"],
                bd=1,
                relief="solid"
            )

            card.grid(
                row=row,
                column=col,
                padx=8,
                pady=8,
                sticky="nsew"
            )

            tk.Label(
                card,
                text="☎",
                bg=self.colors["white"],
                fg=self.colors["red"],
                font=("Arial", 28)
            ).pack(
                pady=(20, 5)
            )

            tk.Label(
                card,
                text=self.display_contact(contact["service"], contact["description"])[0],
                bg=self.colors["white"],
                fg=self.colors["text"],
                font=("Arial", 14, "bold")
            ).pack(
                pady=5
            )

            tk.Label(
                card,
                text=contact["phone"],
                bg=self.colors["white"],
                fg=self.colors["red"],
                font=("Arial", 20, "bold")
            ).pack(
                pady=5
            )

            tk.Label(
                card,
                text=self.display_contact(contact["service"], contact["description"])[1],
                bg=self.colors["white"],
                fg=self.colors["gray"],
                font=("Arial", 9),
                wraplength=350
            ).pack(
                padx=15,
                pady=(5, 10)
            )

            self.make_button(
                card,
                "☎ " + self.t("call_now"),
                self.show_dialer_message,
                self.colors["green"],
                16
            ).pack(pady=(0, 20))

    # ========================================================
    # MANAGE CONTACTS
    # ========================================================

    def manage_contacts(self):

        self.current_screen = self.manage_contacts

        self.clear_screen()

        self.create_header(
            self.t("manage_contacts"),
            self.t("contacts_manage_subtitle")
        )

        main = tk.Frame(
            self.root,
            bg=self.colors["bg"]
        )

        main.pack(
            fill="both",
            expand=True
        )

        self.admin_sidebar(main)

        content = self.create_scrollable_frame_for_parent(main)

        tk.Label(
            content,
            text=self.t("manage_contacts"),
            bg=self.colors["bg"],
            fg=self.colors["dark_blue"],
            font=("Arial", 21, "bold")
        ).pack(
            anchor="w",
            padx=25,
            pady=20
        )

        table_frame = tk.Frame(
            content,
            bg=self.colors["white"]
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=10
        )

        columns = (
            "id",
            "service",
            "phone",
            "description"
        )

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for col in columns:

            tree.heading(
                col,
                text={"id": self.t("id"), "service": self.t("service"), "phone": self.t("phone"), "description": self.t("description")}[col]
            )

            tree.column(
                col,
                width=180,
                anchor="center"
            )

        conn = get_db()

        contacts = conn.execute("""
            SELECT *
            FROM emergency_contacts
        """).fetchall()

        conn.close()

        for contact in contacts:

            tree.insert(
                "",
                "end",
                values=(
                    contact["id"],
                    self.display_contact(contact["service"], contact["description"])[0],
                    contact["phone"],
                    self.display_contact(contact["service"], contact["description"])[1]
                )
            )

        tree.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        buttons = tk.Frame(
            content,
            bg=self.colors["bg"]
        )

        buttons.pack(
            pady=20
        )

        def delete_contact():

            selected = tree.selection()

            if not selected:
                messagebox.showwarning(
                    self.t("warning"),
                    self.t("select_contact")
                )
                return

            values = tree.item(
                selected[0],
                "values"
            )

            if not messagebox.askyesno(
                self.t("confirm"),
                self.t("confirm_delete")
            ):
                return

            conn = get_db()

            conn.execute(
                "DELETE FROM emergency_contacts WHERE id = ?",
                (values[0],)
            )

            conn.commit()
            conn.close()

            self.manage_contacts()

        self.make_button(
            buttons,
            "➕ " + self.t("add_contact"),
            self.add_contact,
            self.colors["green"],
            17
        ).pack(
            side="left",
            padx=5
        )

        self.make_button(
            buttons,
            self.t("delete"),
            delete_contact,
            self.colors["red"],
            17
        ).pack(
            side="left",
            padx=5
        )

    # ========================================================
    # ADD CONTACT
    # ========================================================

    def add_contact(self):

        window = tk.Toplevel(
            self.root
        )

        window.title(
            self.t("add_contact")
        )

        window.geometry(
            "500x450"
        )

        window.configure(
            bg=self.colors["bg"]
        )

        tk.Label(
            window,
            text=self.t("add_contact"),
            bg=self.colors["dark_blue"],
            fg="white",
            font=("Arial", 17, "bold")
        ).pack(
            fill="x",
            pady=15
        )

        form = tk.Frame(
            window,
            bg=self.colors["white"]
        )

        form.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        self.field_label(
            form,
            self.t("service")
        )

        service = self.entry(form)

        self.field_label(
            form,
            self.t("phone")
        )

        phone = self.entry(form)

        self.field_label(
            form,
            self.t("description")
        )

        description = self.entry(form)

        def save():

            if not service.get().strip() or not phone.get().strip():

                messagebox.showwarning(
                    self.t("warning"),
                    self.t("required")
                )

                return

            conn = get_db()

            conn.execute("""
                INSERT INTO emergency_contacts
                (service, phone, description)
                VALUES (?, ?, ?)
            """, (
                service.get().strip(),
                phone.get().strip(),
                description.get().strip()
            ))

            conn.commit()
            conn.close()

            window.destroy()

            self.manage_contacts()

        self.make_button(
            form,
            self.t("save"),
            save,
            self.colors["green"],
            18
        ).pack(
            pady=20
        )

    # ========================================================
    # LOGOUT
    # ========================================================

    def logout(self):

        self.current_user = None
        self.current_admin = None

        self.show_home()


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = EmergencySystem(root)

    root.mainloop()