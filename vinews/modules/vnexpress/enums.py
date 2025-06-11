from enum import Enum
class VnExpressSearchCategory(Enum):
    BUSINESS = "kinhdoanh"
    COMMUNITY = "cong-dong"
    #PODCAST = "podcast"
    LAW = "phap-luat"
    WORLD = "the-gioi"
    TRAVEL = "dulich"
    SCI_TECH = "khoa-hoc-cong-nghe"
    NEWS = "thoi-su"
    VEHICLE = "oto-xe-may"
    SPORTS = "thethao"
    LIFESTYLE = "doisong"
    HEALTH = "suckhoe"

class VnExpressNewsTopics(Enum):
    POLITICS = "chinh-tri"
    HR = "nhan-su"
    SOCIAL_ISSUES = "dan-sinh"
    JOBS = "viec-lam"
    TRAFFIC = "giaothong"
    HOPE_FOUNDATION = "quy-hy-vong"

class VnExpressWorldTopics(Enum):
    DOCUMENTARY = "tu-lieu"
    ANALYTICS = "phan-tich"
    GLOBAL_VN = "nguoi-viet-5-chau"
    GLOBAL_LIFE = "cuoc-song-do-day"
    MILITARY = "quan-su"

class VnExpressBusinessTopics(Enum):
    GLOBAL = "quoc-te"
    BUSINESS = "doanh-nghiep"
    STOCK_MARKET = "chung-khoan"
    EBANK = "ebank"
    MACRO = "vi-mo"
    MY_MONEY = "tien-cua-toi"
    GOODS = "hang-hoa"

class VnExpressSciTechTopics(Enum):
    DIGITAL_TRANSFORMATION = "chuyen-doi-so"
    INNOVATION = "doi-moi-sang-tao"
    AI = "ai"
    SPACE = "vu-tru"
    NATURE = "the-gioi-tu-nhien"
    DEVICES = "thiet-bi"
    KNOWLEDGE = "cua-so-tri-thuc"

class VnExpressEstateTopics(Enum):
    POLICY = "chinh-sach"
    MARKET = "thi-truong"

class VnExpressHealthTopics(Enum):
    NEWS = "tin-tuc"
    DISEASES = "cac-benh"
    LIFESTYLE = "song-khoe"
    VACCINE = "vaccine"

class VnExpressSportsTopics(Enum):
    FOOTBALL = "bong-da"
    TENNIS = "tennis"
    OTHER = "cac-mon-khac"
    CELEBS = "hau-truong"

class VnExpressEntertainmentTopics(Enum):
    CELEBRITY = "sao"
    MOVIES = "phim"
    MUSIC = "nhac"
    FASHION = "thoi-trang"
    BEAUTY = "lam-dep"
    STAGE_ART = "san-khau-my-thuat"

class VnExpressLawTopics(Enum):
    CASE = "ho-so-pha-an"

class VnExpressEduTopics(Enum):
    NEWS = "tin-tuc"
    ADMISSIONS = "tuyen-sinh"
    PROFILES = "chan-dung"
    ABROAD = "du-hoc"
    DISCUSSIONS = "thao-luan"
    ENGLISH = "hoc-tieng-anh"
    EDUCATION_40 = "giao-duc-40"

class VnExpressLifestyleTopics(Enum):
    BIORHYTHM = "nhip-song"
    FAMILY = "to-am"
    LIFE_LESSION = "bai-hoc-song"
    CONSUMER = "tieu-dung"

class VnExpressVehicleTopics(Enum):
    MARKET = "thi-truong"
    STUDY = "cam-lai"

class VnExpressTravelTopics(Enum):
    DESTINATIONS = "diem-den"
    FOOD = "am-thuc"
    FOOTPRINTS = "dau-chan"
    