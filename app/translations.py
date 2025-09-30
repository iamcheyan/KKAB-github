"""Simple translation mappings for the GuestHouse site.

支持从 JSON 配置覆盖：若存在 `app/data/i18n.json`，将以其中的
- languages: 覆盖可用语言列表
- default:   覆盖默认语言
- translations: 合并键值（不存在的键将新增，已存在的语言键将覆盖）
"""

from __future__ import annotations

LANGUAGES = ["ja", "en", "zh"]
DEFAULT_LANGUAGE = "ja"


TRANSLATIONS = {
    "nav.home": {
        "ja": "ホーム",
        "en": "Home",
        "zh": "首页",
    },
    "nav.rooms": {"ja": "客室", "en": "Rooms", "zh": "客房"},
    "nav.booking": {"ja": "予約", "en": "Booking", "zh": "预订"},
    "nav.contact": {"ja": "お問い合わせ", "en": "Contact", "zh": "联系我们"},
    "nav.admin": {"ja": "管理", "en": "Admin", "zh": "后台"},
    "nav.management": {"ja": "運営代行", "en": "Management", "zh": "运营代管"},
    "lang.ja": {"ja": "日本語", "en": "Japanese", "zh": "日语"},
    "lang.en": {"ja": "英語", "en": "English", "zh": "英语"},
    "lang.zh": {"ja": "中国語", "en": "Chinese", "zh": "中文"},
    "footer.tagline": {
        "ja": "京都の静かな路地で、ゆったりとしたひとときを。",
        "en": "In the quiet backstreets of Kyoto, enjoy a moment of serenity.",
        "zh": "在京都的静谧小巷里，体验悠然的时光。",
    },
    "hero.kicker": {
        "ja": "KYOTO ",
        "en": "KYOTO ",
        "zh": "京都 ",
    },
    "hero.title": {
        "ja": "京都の宿泊施設で、\n静かに息を整える宿",
        "en": "Kyoto accommodations\nfor your peaceful stay",
        "zh": "京都住宿设施，\n专属一人的静谧时光",
    },
    "hero.subtitle": {
        "ja": "は京都各地に展開する多様な宿泊施設を提供しています。一棟貸しの町家から現代的なアパートまで、ご旅行スタイルに合わせてお選びいただけます。",
        "en": "We offer diverse accommodations across Kyoto. From traditional machiya townhouses to modern apartments, choose the perfect stay for your travel style.",
        "zh": "在京都各地提供多样化的住宿选择。从整栋町家到现代公寓，根据您的旅行风格自由选择。",
    },
    "hero.cta_book": {"ja": "ご予約はこちら", "en": "Book Your Stay", "zh": "立即预订"},
    "hero.cta_rooms": {"ja": "客室を見る", "en": "View Rooms", "zh": "查看客房"},
    "hero.badge": {
        "ja": "多様な宿泊タイプをご用意",
        "en": "Multiple accommodation types available",
        "zh": "提供多种住宿类型",
    },
    "hero.point1": {
        "ja": "一棟貸しからアパートまで多様な選択肢",
        "en": "Diverse options from traditional machiya to modern apartments",
        "zh": "从整栋町家到现代公寓的多样化选择",
    },
    "hero.point2": {
        "ja": "京都駅近くから鴨川沿いまで好立地",
        "en": "Prime locations from near Kyoto Station to riverside",
        "zh": "从京都站附近到鸭川沿岸的优越位置",
    },
    "hero.point3": {
        "ja": "一人旅から家族旅行まで対応",
        "en": "Perfect for solo travelers to family trips",
        "zh": "适合从个人旅行到家庭出游",
    },
    "hero.info.hours": {
        "ja": "多様な宿泊タイプをご用意しています",
        "en": "Multiple accommodation options available",
        "zh": "多种房源可供选择",
    },
    "hero.info.station": {
        "ja": "一戸建てタイプもあり、ご家族での滞在に最適です",
        "en": "Detached house available, ideal for families",
        "zh": "提供一户建房源，满足全家居住需要",
    },
    "stay.kicker": {
        "ja": "STAY IN KYOTO",
        "en": "STAY IN KYOTO",
        "zh": "京都旅行",
    },
    "stay.title": {
        "ja": "季節の息遣いと職人の手仕事を感じる滞在",
        "en": "Experience the seasons and Kyoto craftsmanship",
        "zh": "感受京都四季与职人手作的旅程",
    },
    "stay.subtitle": {
        "ja": "春は桜の香、夏は川床の涼、秋は紅葉の光、冬は炭火の温度。五感で京都を味わう時間をご用意しております。",
        "en": "Spring brings sakura fragrance, summer the cool river breeze, autumn glowing foliage, and winter the warmth of charcoal. Every stay is curated to savour Kyoto with all five senses.",
        "zh": "春品樱香，夏听川风，秋赏红叶，冬享炭火。让五感在京都得到细致的款待。",
    },
    "stay.morning.title": {
        "ja": "朝の茶会と季節の和朝食",
        "en": "Morning tea ceremony & seasonal breakfast",
        "zh": "晨间茶会与四季和风早餐",
    },
    "stay.morning.body": {
        "ja": "茶道講師と過ごす朝の点前体験と、京野菜・おばんざいを中心とした和朝食を、町家の土間にてご提供します。",
        "en": "Begin the day with a tea master-led ceremony and a Kyoto-style breakfast of seasonal vegetables served in the machiya doma.",
        "zh": "与茶道讲师一同体验晨间点前，并在町家土间享用以京野菜与家常菜为主的和风早餐。",
    },
    "stay.interior.title": {
        "ja": "工芸と現代デザインの調和",
        "en": "Craftsmanship meets modern design",
        "zh": "工艺与现代设计的平衡",
    },
    "stay.interior.body": {
        "ja": "伝統的な意匠と現代的な快適さを兼ね備えた空間でお過ごしいただけます。",
        "en": "Enjoy a space that blends traditional design with modern comfort.",
        "zh": "在融合传统设计与现代舒适的空间中度过美好时光。",
    },
    "stay.experience.title": {
        "ja": "町散策と非公開寺院の拝観",
        "en": "Hidden walks & private temple visits",
        "zh": "巷弄漫步与寺院私享参观",
    },
    "stay.experience.body": {
        "ja": "宿専属のコンシェルジュが、路地散歩や庭園拝観、季節の行事など、旅のテーマに合わせてご案内いたします。",
        "en": "Our concierge crafts itineraries of alleyway strolls, garden viewings, and seasonal rituals tailored to your interests.",
        "zh": "专属礼宾将依照旅程主题安排巷弄散步、庭园参访与季节活动。",
    },
    "rooms.kicker": {
        "ja": "客室",
        "en": "ROOMS",
        "zh": "客房",
    },
    "rooms.title": {
        "ja": "京都宿泊施設のご案内",
        "en": "Kyoto Accommodation Options",
        "zh": "京都住宿设施",
    },
    "rooms.subtitle": {
        "ja": "京都各地の多様な宿泊施設をご用意しています。一棟貸しの町家から現代的なアパートまで、お客様のニーズに合わせてお選びいただけます。",
        "en": "We offer diverse accommodations across Kyoto. From traditional machiya townhouses to modern apartments, choose what suits your travel needs.",
        "zh": "在京都各地提供多样化的住宿选择。从整栋町家到现代公寓，根据您的需求自由选择。",
    },
    "rooms.capacity": {
        "ja": "定員 {count} 名様",
        "en": "Capacity {count} guests",
        "zh": "容纳 {count} 人",
    },
    "rooms.included": {
        "ja": "多様な宿泊タイプ",
        "en": "Multiple accommodation types",
        "zh": "多种住宿类型",
    },
    "rooms.button.details": {"ja": "詳細を見る", "en": "View Details", "zh": "查看详情"},
    "rooms.button.back_to_rooms": {"ja": "宿泊施設一覧に戻る", "en": "Back to Rooms", "zh": "返回房间列表"},
    "rooms.detail.about": {"ja": "宿泊施設のご案内", "en": "About this accommodation", "zh": "住宿介绍"},
    "rooms.detail.address_label": {"ja": "所在地", "en": "Address", "zh": "地址"},
    "rooms.detail.permit_label": {"ja": "許可番号", "en": "Permit No.", "zh": "许可编号"},
    "rooms.detail.status_label": {"ja": "現在の状況", "en": "Current status", "zh": "当前状态"},
    "rooms.detail.book_airbnb": {"ja": "Airbnbで予約する", "en": "Book on Airbnb", "zh": "在Airbnb预订"},
    "rooms.detail.back_to_list": {"ja": "一覧へ戻る", "en": "Back to list", "zh": "返回列表"},
    "rooms.alert.empty": {
        "ja": "現在ご案内できる宿泊施設がございません。",
        "en": "No accommodations are available at the moment.",
        "zh": "目前暂无可预订的住宿设施。",
    },
    "essence.kicker": {"ja": "KYOTO ESSENCE", "en": "KYOTO ESSENCE", "zh": "京都精髓"},
    "essence.title": {
        "ja": "町家で味わう、京都らしさの断片",
        "en": "Fragments of Kyoto to savour within the machiya",
        "zh": "在町家里品味京都的片刻",
    },
    "essence.lighting.title": {
        "ja": "灯りと香りの演出",
        "en": "Lighting & Fragrance",
        "zh": "灯光与香氛",
    },
    "essence.lighting.body": {
        "ja": "日が暮れると、行灯と香木の香りが土間を満たし、京都の夜にふさわしい静けさが訪れます。月替わりの調香で旅の記憶を彩ります。",
        "en": "At dusk, lanterns and incense fill the doma with serenity. Monthly fragrances keep your Kyoto memories vivid.",
        "zh": "夜幕降临，行灯与香木弥漫土间，为京都之夜添上静谧。每月更换的香气为旅程留下独特记忆。",
    },
    "essence.sweets.title": {
        "ja": "京菓子とのおもてなし",
        "en": "Welcome sweets",
        "zh": "京菓款待",
    },
    "essence.sweets.body": {
        "ja": "老舗和菓子店と共同でつくるオリジナルの干菓子と抹茶をご用意。季節の花や行事に合わせたしつらえでお迎えします。",
        "en": "Enjoy original confections created with a historic wagashi shop, paired with matcha and seasonal displays.",
        "zh": "与老字号和菓子店联手制作原创干菓与抹茶，并以应季花器与陈设迎宾。",
    },
    "essence.concierge.title": {
        "ja": "旅のコンシェルジュ",
        "en": "Travel concierge",
        "zh": "旅程礼宾",
    },
    "essence.concierge.body": {
        "ja": "早朝の寺院拝観や、京友禅の型染め体験、町家でのライブ演奏など、ご要望に合わせた特別な時間を手配いたします。",
        "en": "From dawn temple visits to yuzen dye workshops and townhouse concerts, we arrange experiences tailored to you.",
        "zh": "无论是清晨参拜、京友禅染体验或町家音乐会，我们都会为您量身安排。",
    },
    "callout.title": {
        "ja": "京都での滞在を丁寧に設計いたします",
        "en": "Let us design your Kyoto stay with care",
        "zh": "为您细致规划京都之旅",
    },
    "callout.body": {
        "ja": "ご希望のテーマや日程をお知らせください。町家コンシェルジュが最適なプランをご提案し、予約から当日のご案内までサポートいたします。",
        "en": "Share your preferred themes and schedule. Our concierge will craft the ideal plan and assist from booking to check-out.",
        "zh": "告诉我们您的行程主题与日期。礼宾团队将从预订到入住全程协助。",
    },
    "callout.cta_book": {"ja": "宿泊を予約する", "en": "Reserve Now", "zh": "立即预订"},
    "callout.cta_contact": {"ja": "お問い合わせ", "en": "Contact Us", "zh": "联络我们"},
    "management.kicker": {"ja": "MINPAKU OPS", "en": "MINPAKU OPS", "zh": "民泊运营"},
    "management.hero.title": {
        "ja": "民泊の運営代行をワンストップで",
        "en": "One‑stop management for minpaku operations",
        "zh": "一站式民泊运营代管"
    },
    "management.hero.lead": {
        "ja": "Airbnb運用・無人運営体制・清掃管理まで、収益最大化を支援します。",
        "en": "From OTA ops and unmanned workflows to housekeeping, we maximize returns.",
        "zh": "从平台运营、无人化流程到清扫维护，助力收益最大化。"
    },
    "management.cta_consult": {"ja": "無料で相談する", "en": "Free consultation", "zh": "免费咨询"},
    "management.button.view_rooms": {"ja": "宿泊施設を見る", "en": "View Rooms", "zh": "查看住宿设施"},
    "management.feature.1.title": {"ja": "手間ゼロの安心運営", "en": "Hassle‑free ops", "zh": "省心运营"},
    "management.feature.1.body": {
        "ja": "開業準備から法令対応・ゲスト対応まで代行。初めてでも安心です。",
        "en": "We handle setup, compliance and guest support. Great for first‑timers.",
        "zh": "代办开业、合规与客服，初次也放心。"
    },
    "management.feature.2.title": {"ja": "インバウンドに強い集客", "en": "Inbound‑strong marketing", "zh": "强力引流"},
    "management.feature.2.body": {
        "ja": "Airbnb/Booking.com の運用最適化で客室販売を強化。",
        "en": "Airbnb/Booking.com optimization boosts sales.",
        "zh": "优化 Airbnb/Booking.com 提升转化。"
    },
    "management.feature.3.title": {"ja": "清掃品質とレビュー改善", "en": "Quality cleaning & reviews", "zh": "清扫品质与评价"},
    "management.feature.3.body": {
        "ja": "チェックリスト運用で品質を担保。高評価レビューを獲得。",
        "en": "Checklist‑driven QA secures high guest ratings.",
        "zh": "清单化质检，稳定高分评价。"
    },
    "management.flow.title": {"ja": "開業までの流れ", "en": "Flow to launch", "zh": "开业流程"},
    "management.flow.items": {
        "ja": "ヒアリング→ご提案→契約→開業準備→開業",
        "en": "Discovery → Proposal → Contract → Preparation → Launch",
        "zh": "沟通 → 方案 → 合同 → 准备 → 开业"
    },
    "management.intro.heading": {
        "ja": "民泊運営代行サービス",
        "en": "Comprehensive Minpaku Management",
        "zh": "民泊运营代管服务"
    },
    "management.intro.lead": {
        "ja": "物件選定からオペレーション、集客までワンストップでサポートします。",
        "en": "From property selection to operations and marketing, we support you end-to-end.",
        "zh": "从物件选定到运营与集客，我们提供一站式支援。"
    },
    "management.intro.body": {
        "ja": "地域特性と法令を踏まえた物件診断、収益シミュレーション、無人運営のノウハウを組み合わせ、オーナー様の手間を最大限削減します。",
        "en": "We combine local compliance checks, revenue simulation and unmanned operation know‑how to minimize owner burden.",
        "zh": "结合地域合规检查、收益模拟与无人化运营经验，为房东最大限度降低运营负担。"
    },
    "management.feature.1.detail": {
        "ja": "法令確認・許認可の支援、現地調査や消防設備の設置手配など、開業に必要な手続きを一括で代行します。",
        "en": "We handle permits, local surveys and equipment setup required to launch safely.",
        "zh": "我们代办许可、现场调查与消防设施安装等开业所需事项。"
    },
    "management.feature.2.detail": {
        "ja": "競合分析や価格戦略で稼働率とADRを改善し、最大収益を目指します。",
        "en": "We improve occupancy and ADR through competitor analysis and dynamic pricing.",
        "zh": "通过竞品分析与动态定价提升出租率与平均房价，实现收益最大化。"
    },
    "management.feature.3.detail": {
        "ja": "地域密着の清掃チームと写真管理による品質担保、ゲスト満足度向上を目指します。",
        "en": "Local cleaning teams, photo‑verified QA and review management keep quality high.",
        "zh": "由当地清洁团队与照片核查确保品质，并提升住客评价。"
    },
    "management.services.title": {
        "ja": "提供サービス",
        "en": "Our Services",
        "zh": "提供的服务"
    },
    "management.services.subtitle": {
        "ja": "開業前〜運営中まで、段階ごとに必要なサービスを用意しています。",
        "en": "We provide the right services at each stage from pre‑launch to ongoing ops.",
        "zh": "从开业前到运营中，我们按阶段提供所需服务。"
    },
    "management.services.item1.title": {"ja": "事業計画", "en": "Business Planning", "zh": "事业计划"},
    "management.services.item1.body": {"ja": "市場・収支の分析を行い現実的な計画を策定します。", "en": "Market & P&L analysis for realistic planning.", "zh": "进行市场与收支分析，制定可行计划。"},
    "management.services.item2.title": {"ja": "エリア・市場分析", "en": "Area & Market Analysis", "zh": "区域与市场分析"},
    "management.services.item2.body": {"ja": "周辺需要や条例を踏まえて物件のポテンシャルを診断します。", "en": "Assess property potential considering demand and regulations.", "zh": "结合周边需求与法规评估物件潜力。"},
    "management.services.item3.title": {"ja": "初期費用算出", "en": "Initial Cost Estimation", "zh": "初期费用计算"},
    "management.services.item3.body": {"ja": "許認可・改修・設備費等の見積りを提示します。", "en": "We provide estimates for permits, renovation and equipment.", "zh": "提供许可、改修与设备费用估算。"},
    "management.services.item4.title": {"ja": "収支シミュレーション", "en": "Revenue Simulation", "zh": "收益模拟"},
    "management.services.item4.body": {"ja": "開業後の年間収支予測を提示します。", "en": "Forecast annual revenues post‑launch.", "zh": "提供开业后的年度收益预测。"},
    "management.services.item5.title": {"ja": "物件コンセプト立案", "en": "Property Concepting", "zh": "物件概念规划"},
    "management.services.item5.body": {"ja": "ターゲットに合わせた内装・運営コンセプトを策定します。", "en": "Concepts for interior & operations tailored to your target guests.", "zh": "为目标客群制定内装与运营概念。"},
    "management.services.item6.title": {"ja": "オペレーション構築", "en": "Ops Setup", "zh": "运营构建"},
    "management.services.item6.body": {"ja": "チェックイン・清掃・備品管理の仕組みを整えます。", "en": "Set up check‑in, cleaning and inventory processes.", "zh": "建立入住、清洁与物资管理流程。"},
    "management.services.item7.title": {"ja": "清掃管理", "en": "Housekeeping Management", "zh": "清洁管理"},
    "management.services.item7.body": {"ja": "地域のプロ業者と協力し品質を維持します。", "en": "Partnering with local pros to maintain high standards.", "zh": "与当地专业团队合作以维持品质。"},
    "management.services.item8.title": {"ja": "OTA運用・集客", "en": "OTA Ops & Marketing", "zh": "OTA运营与集客"},
    "management.services.item8.body": {"ja": "各OTA最適化と価格戦略で集客力を高めます。", "en": "Optimize OTA listings and pricing to increase demand.", "zh": "优化 OTA 刊登与定价以提高吸引力。"},
    "management.cases.title": {"ja": "運営実績", "en": "Case Studies", "zh": "运营实绩"},
    "management.case1.title": {"ja": "YANAKA SOW", "en": "YANAKA SOW", "zh": "YANAKA SOW"},
    "management.case1.body": {"ja": "商品企画から設計・開業まで一括支援した一棟ホテル案件。", "en": "End‑to‑end support for a converted townhouse hotel.", "zh": "从企划到开业的一栋酒店项目的一体化支援。"},
    "management.case2.title": {"ja": "長者丸ビル", "en": "Chojamaru Building", "zh": "长者丸大楼"},
    "management.case2.body": {"ja": "賃貸をホテルへ転用し資産価値を向上させた事例。", "en": "Renovation conversion increasing asset value.", "zh": "将闲置租赁改造为酒店并提升资产价值的案例。"},
    "management.case3.title": {"ja": "Live Casa Tokyo浜松町", "en": "Live Casa Tokyo Hamamatsucho", "zh": "Live Casa Tokyo滨松町"},
    "management.case3.body": {"ja": "マンスリー運用と組み合わせ安定収益を確保した事例。", "en": "Hybrid monthly operation yielding stable revenue.", "zh": "通过与月租结合实现稳定收益的案例。"},
    "management.cta_title": {"ja": "まずは無料相談から", "en": "Start with a free consultation", "zh": "先从免费咨询开始"},
    "management.cta_body": {"ja": "物件の簡易診断は無料で承ります。収支シミュレーションや運営プランをお気軽にご相談ください。", "en": "We offer free basic property assessments. Ask us for revenue sims and operations plans.", "zh": "我们提供免费的基础物件评估。欢迎咨询收益模拟与运营方案。"},
    "rooms.list.intro.title": {
        "ja": "京都宿泊施設のご案内",
        "en": "Kyoto Accommodation Options",
        "zh": "京都住宿设施",
    },
    "rooms.list.intro.text": {
        "ja": "京都各地の多様な宿泊施設をご用意しています。一棟貸しの町家から現代的なアパートまで、お客様のニーズに合わせてお選びいただけます。",
        "en": "We offer diverse accommodations across Kyoto. From traditional machiya townhouses to modern apartments, choose what suits your travel needs.",
        "zh": "在京都各地提供多样化的住宿选择。从整栋町家到现代公寓，根据您的需求自由选择。",
    },
    "rooms.list.cta": {"ja": "宿泊予約へ", "en": "Request Booking", "zh": "提交预订"},
    "rooms.recommendations.title": {
        "ja": "おすすめの宿泊施設",
        "en": "Recommended Accommodations",
        "zh": "推荐房源"
    },
    "rooms.recommendations.subtitle": {
        "ja": "他にも魅力的な宿泊施設をご用意しています",
        "en": "We have other attractive accommodations available",
        "zh": "我们还为您准备了其他优质的住宿选择"
    },
    "rooms.view_all": {
        "ja": "すべての客室を見る",
        "en": "View All Rooms",
        "zh": "查看所有客房"
    },
    "rooms.facilities.title": {
        "ja": "施設・サービス",
        "en": "Facilities & Services",
        "zh": "设施与服务"
    },
    "rooms.facilities.wifi": {
        "ja": "高速Wi-Fi",
        "en": "High-Speed WiFi",
        "zh": "高速Wi-Fi"
    },
    "rooms.facilities.wifi_desc": {
        "ja": "全室無料Wi-Fi完備",
        "en": "Free WiFi throughout the property",
        "zh": "全房免费Wi-Fi覆盖"
    },
    "rooms.facilities.location": {
        "ja": "好立地",
        "en": "Prime Location",
        "zh": "优越位置"
    },
    "rooms.facilities.location_desc": {
        "ja": "近隣駅から徒歩圏内",
        "en": "Walking distance to nearby stations",
        "zh": "步行可达附近地铁站"
    },
    "rooms.facilities.space": {
        "ja": "広々とした空間",
        "en": "Spacious Living",
        "zh": "宽敞空间"
    },
    "rooms.facilities.space_desc": {
        "ja": "ゆったりとした居住空間",
        "en": "Comfortable living space",
        "zh": "舒适的居住空间"
    },
    "rooms.facilities.safety": {
        "ja": "安全・安心",
        "en": "Safe & Secure",
        "zh": "安全可靠"
    },
    "rooms.facilities.safety_desc": {
        "ja": "24時間セキュリティ",
        "en": "24-hour security",
        "zh": "24小时安全保障"
    },
    "rooms.booking_info.title": {
        "ja": "ご利用案内",
        "en": "Booking Information",
        "zh": "预订须知"
    },
    "rooms.booking_info.airbnb_title": {
        "ja": "Airbnbでご確認ください",
        "en": "Please check on Airbnb",
        "zh": "请参考Airbnb页面"
    },
    "rooms.booking_info.airbnb_description": {
        "ja": "詳細な利用条件・料金・空室状況はAirbnbページでご確認ください",
        "en": "Please check Airbnb page for detailed terms, rates, and availability",
        "zh": "详细的入住条件、价格、空房情况请参考Airbnb页面"
    },
    "rooms.booking_info.checkin": {
        "ja": "チェックイン",
        "en": "Check-in",
        "zh": "入住时间"
    },
    "rooms.booking_info.checkin_time": {
        "ja": "参考時間（要事前連絡）",
        "en": "Reference time (advance notice required)",
        "zh": "参考时间（需提前联系）"
    },
    "rooms.booking_info.checkout": {
        "ja": "チェックアウト",
        "en": "Check-out",
        "zh": "退房时间"
    },
    "rooms.booking_info.checkout_time": {
        "ja": "参考時間",
        "en": "Reference time",
        "zh": "参考时间"
    },
    "rooms.booking_info.guests": {
        "ja": "宿泊人数",
        "en": "Guest Capacity",
        "zh": "住宿人数"
    },
    "rooms.booking_info.guests_info": {
        "ja": "参考定員",
        "en": "Reference capacity",
        "zh": "参考人数"
    },
    "rooms.booking_info.policy": {
        "ja": "キャンセルポリシー",
        "en": "Cancellation Policy",
        "zh": "取消政策"
    },
    "rooms.booking_info.policy_info": {
        "ja": "Airbnbでご確認ください",
        "en": "Please check on Airbnb",
        "zh": "请参考Airbnb页面"
    },
    "rooms.booking_info.note": {
        "ja": "※ 最新の料金・空室状況・利用条件はAirbnbページをご確認ください",
        "en": "※ Please check Airbnb page for latest rates, availability and terms",
        "zh": "※ 最新价格、空房情况、使用条件请参考Airbnb页面"
    },
    "rooms.house_rules.title": {
        "ja": "ハウスルール",
        "en": "House Rules",
        "zh": "房屋规则"
    },
    "rooms.house_rules.respect": {
        "ja": "宿泊施設はホストなどの自宅であることも多いため、敬意を払い、大切に扱ってください。",
        "en": "Please treat the accommodation with respect as it may be the host's home.",
        "zh": "住宿设施可能是房东的自宅，请以敬意对待并妥善保管。"
    },
    "rooms.house_rules.checkin_out": {
        "ja": "チェックイン・チェックアウト",
        "en": "Check-in & Check-out",
        "zh": "入住与退房"
    },
    "rooms.house_rules.checkin_time": {
        "ja": "チェックイン時刻：15:00以降",
        "en": "Check-in time: After 15:00",
        "zh": "入住时间：15:00以后"
    },
    "rooms.house_rules.checkout_time": {
        "ja": "チェックアウト時刻：10:00前",
        "en": "Check-out time: Before 10:00",
        "zh": "退房时间：10:00前"
    },
    "rooms.house_rules.self_checkin": {
        "ja": "セルフチェックイン（キーボックス）",
        "en": "Self check-in (keybox)",
        "zh": "自助入住（钥匙盒）"
    },
    "rooms.house_rules.before_checkout": {
        "ja": "チェックアウトする前に",
        "en": "Before check-out",
        "zh": "退房前请"
    },
    "rooms.house_rules.turn_off_power": {
        "ja": "電源をオフにする",
        "en": "Turn off power",
        "zh": "关闭电源"
    },
    "rooms.house_rules.return_key": {
        "ja": "鍵を返す",
        "en": "Return the key",
        "zh": "归还钥匙"
    },
    "rooms.house_rules.lock_door": {
        "ja": "鍵をかける",
        "en": "Lock the door",
        "zh": "锁好门"
    },
    "rooms.facility.bath": {
        "ja": "坪庭を望む檜風呂と足湯",
        "en": "Hinoki bath and foot soak facing the courtyard",
        "zh": "眺望坪庭的桧木浴与足汤",
    },
    "rooms.facility.textile": {
        "ja": "伝統工芸のファブリックと和紙の照明",
        "en": "Traditional fabrics & washi lighting",
        "zh": "传统织物与和纸灯具",
    },
    "rooms.facility.bedding": {
        "ja": "オーガニック素材の寝具、加湿器完備",
        "en": "Organic bedding with humidifier",
        "zh": "有机寝具与加湿设备",
    },
    "rooms.facility.tea": {
        "ja": "京番茶とオリジナルブレンドの煎茶セット",
        "en": "Kyobancha and house-blend sencha set",
        "zh": "京番茶与原创煎茶组合",
    },
    "rooms.facility.amenities": {
        "ja": "今治タオル・オーガニックコスメ一式",
        "en": "Imabari towels & organic bath amenities",
        "zh": "今治毛巾与有机浴品",
    },
    "rooms.facility.drinks": {
        "ja": "エスプレッソマシンと京番茶の茶筒",
        "en": "Espresso machine & kyobancha canister",
        "zh": "意式咖啡机与京番茶茶筒",
    },
    "rooms.facility.audio": {
        "ja": "BOSE サウンドシステム・Wi-Fi完備",
        "en": "BOSE sound system & high-speed Wi-Fi",
        "zh": "BOSE 音响与高速 Wi-Fi",
    },
    "rooms.facility.air": {
        "ja": "加湿空気清浄機・床暖房（冬季）",
        "en": "Humidifying air purifier & floor heating (winter)",
        "zh": "加湿空气净化器与地暖（冬季）",
    },
    "rooms.facility.plan": {
        "ja": "15:00 チェックイン → 16:00 町家でゆったり → 18:00 京懐石のお弁当 → 21:00 足湯でリラックス → 翌朝 茶会と和朝食。",
        "en": "15:00 check-in → 16:00 relax in your private machiya → 18:00 Kyoto kaiseki bento → 21:00 foot bath unwind → Morning tea ceremony & breakfast.",
        "zh": "15:00 办理入住 → 16:00 町家休憩 → 18:00 京都怀石便当 → 21:00 足汤放松 → 次晨茶会与和风早餐。",
    },
    "rooms.facility.plan_note": {
        "ja": "早朝の寺院拝観や特別な体験も手配可能です。",
        "en": "We can also arrange early-morning temple visits or special experiences upon request.",
        "zh": "亦可应需求安排清晨寺院参拜或特别体验。",
    },
    "rooms.detail.book": {"ja": "この一棟を予約する", "en": "Request this house", "zh": "预订整栋"},
    "rooms.detail.inquire": {"ja": "滞在の相談をする", "en": "Consult us", "zh": "咨询行程"},
    "rooms.list.view_all": {
        "ja": "すべての宿泊施設を見る",
        "en": "View All Stays",
        "zh": "查看全部房源",
    },
    "booking.title": {"ja": "宿泊リクエスト", "en": "Booking Request", "zh": "住宿申请"},
    "booking.intro": {
        "ja": "以下のフォームにご記入ください。空室状況を確認の上、24時間以内にメールにてご連絡いたします。",
        "en": "Fill in the form and we will confirm availability within 24 hours via email.",
        "zh": "请填写下列表格，我们会在24小时内以邮件回复房态。",
    },
    "booking.room": {"ja": "宿泊タイプ", "en": "Stay Type", "zh": "住宿类型"},
    "booking.guests": {"ja": "ご利用人数", "en": "Guests", "zh": "入住人数"},
    "booking.check_in": {"ja": "チェックイン", "en": "Check-in", "zh": "入住日期"},
    "booking.check_out": {"ja": "チェックアウト", "en": "Check-out", "zh": "退房日期"},
    "booking.name": {"ja": "お名前", "en": "Name", "zh": "姓名"},
    "booking.email": {"ja": "メールアドレス", "en": "Email", "zh": "邮箱"},
    "booking.submit": {"ja": "送信", "en": "Submit", "zh": "发送"},
    "booking.flash.success": {
        "ja": "ご予約内容を受け付けました。担当者より追ってご連絡いたします。",
        "en": "Your request has been received. Our concierge will contact you shortly.",
        "zh": "我们已收到您的预订，工作人员将尽快与您联系。",
    },
    "booking.error.room_missing": {
        "ja": "選択した宿泊タイプが見つかりません",
        "en": "The selected stay type could not be found.",
        "zh": "未找到所选住宿类型。",
    },
    "booking.error.over_capacity": {
        "ja": "定員を超えています",
        "en": "Number of guests exceeds capacity.",
        "zh": "入住人数超过上限。",
    },
    "booking.success.title": {
        "ja": "ご予約を承りました",
        "en": "Booking Request Received",
        "zh": "预订已提交",
    },
    "booking.success.message": {
        "ja": "ご予約いただきありがとうございます。空室状況を確認のうえ、コンシェルジュより折り返しご連絡いたします。",
        "en": "Thank you for your booking. We will confirm availability and follow up shortly.",
        "zh": "感谢您的预订。我们将确认房态并尽快与您联系。",
    },
    "booking.success.back": {"ja": "トップへ戻る", "en": "Back to Home", "zh": "返回首页"},
    "contact.heading": {
        "ja": "お問い合わせ",
        "en": "Contact",
        "zh": "联系我们",
    },
    "contact.intro": {
        "ja": "滞在プランのカスタマイズ、特別な体験の手配など、お気軽にお知らせください。24時間以内にコンシェルジュよりご連絡いたします。",
        "en": "Let us know how we can tailor your stay or arrange special experiences. Our concierge will reply within 24 hours.",
        "zh": "如需定制行程或安排特别体验，请随时告知，我们会在24小时内回复。",
    },
    "contact.form.name": {"ja": "お名前", "en": "Name", "zh": "姓名"},
    "contact.form.email": {"ja": "メールアドレス", "en": "Email", "zh": "邮箱"},
    "contact.form.message": {"ja": "お問い合わせ内容", "en": "Message", "zh": "留言内容"},
    "contact.form.submit": {"ja": "送信する", "en": "Send", "zh": "发送"},
    "contact.info.title": {
        "ja": "施設情報",
        "en": "Property Details",
        "zh": "设施信息",
    },
    "contact.info.phone": {"ja": "電話", "en": "Phone", "zh": "电话"},
    "contact.info.email": {"ja": "メール", "en": "Email", "zh": "邮箱"},
    "contact.info.wechat": {"ja": "WeChat QRコード", "en": "WeChat QR Code", "zh": "微信二维码"},
    "contact.info.line": {"ja": "LINE QRコード", "en": "LINE QR Code", "zh": "LINE 二维码"},
    "contact.info.access": {"ja": "アクセス", "en": "Access", "zh": "交通"},
    "contact.access.list1": {
        "ja": "京阪本線「清水五条」駅 3番出口より徒歩7分",
        "en": "7 min walk from Keihan Kiyomizu-Gojo Station (Exit 3)",
        "zh": "京阪“清水五条”3号出口步行7分钟",
    },
    "contact.access.list2": {
        "ja": "京都駅からタクシーで約10分",
        "en": "Approx. 10 min by taxi from Kyoto Station",
        "zh": "从京都站乘坐出租车约10分钟",
    },
    "contact.access.list3": {
        "ja": "駐車場は近隣コインパーキングをご案内します",
        "en": "Nearby coin parking available upon request",
        "zh": "可引导您使用附近投币停车场",
    },
    "contact.flash.success": {
        "ja": "お問い合わせを送信しました。24時間以内にご連絡いたします。",
        "en": "Thank you for your enquiry. We will respond within 24 hours.",
        "zh": "留言已送出，我们会在24小时内回复。",
    },
    "room.status.available": {"ja": "空室あり", "en": "Available", "zh": "可预订"},
    "room.status.booked": {"ja": "満室", "en": "Fully booked", "zh": "已订满"},
    "room.status.prep": {"ja": "準備中", "en": "Preparing", "zh": "准备中"},
    "booking.status.pending": {"ja": "確認待ち", "en": "Pending", "zh": "待确认"},
    "booking.status.confirmed": {"ja": "確定", "en": "Confirmed", "zh": "已确认"},
    "booking.status.cancelled": {"ja": "キャンセル", "en": "Cancelled", "zh": "已取消"},
    "news.section.title": {
        "ja": "お知らせ",
        "en": "News",
        "zh": "公告",
    },
    "news.read_more": {"ja": "詳しく読む", "en": "Read more", "zh": "查看详情"},
    "chat.prompt": {
        "ja": "WeChatで宿主に相談",
        "en": "Chat with host on WeChat",
        "zh": "加微信与房东联系",
    },
    "chat.scan": {
        "ja": "QRコードを読み取ってメッセージをお送りください。",
        "en": "Scan the QR code to message us on WeChat.",
        "zh": "扫描二维码，与房东微信联系。",
    },
    "errors.required": {
        "ja": "必須項目です",
        "en": "This field is required.",
        "zh": "此项为必填。",
    },
    "errors.email": {
        "ja": "正しいメールアドレスを入力してください",
        "en": "Please provide a valid email address.",
        "zh": "请输入有效的电子邮箱。",
    },
    "errors.min_one": {
        "ja": "1名以上で入力してください",
        "en": "Please enter at least one guest.",
        "zh": "请输入至少一位入住人数。",
    },
    "errors.date_order": {
        "ja": "チェックアウト日はチェックイン日より後の日付をお選びください",
        "en": "Check-out must be after check-in.",
        "zh": "退房日期需晚于入住日期。",
    },
    "errors.future_date": {
        "ja": "本日以降の日付をお選びください",
        "en": "Please choose a future date.",
        "zh": "请选择今天之后的日期。",
    },
}

# 可选：从 JSON 配置覆盖语言列表与翻译
try:  # 在导入期执行，失败则静默回落到内置字典
    import os
    import json

    _base_dir = os.path.dirname(__file__)
    _json_path = os.path.join(_base_dir, "data", "i18n.json")
    if os.path.exists(_json_path):
        with open(_json_path, "r", encoding="utf-8") as _fp:
            _cfg = json.load(_fp) or {}

        _langs = _cfg.get("languages")
        if isinstance(_langs, list) and _langs:
            LANGUAGES = [str(x) for x in _langs]

        _default = _cfg.get("default")
        if isinstance(_default, str) and _default:
            DEFAULT_LANGUAGE = _default

        _overrides = _cfg.get("translations") or {}
        if isinstance(_overrides, dict):
            for _key, _val in _overrides.items():
                if not isinstance(_val, dict):
                    continue
                _existing = TRANSLATIONS.get(_key, {})
                _existing.update({k: v for k, v in _val.items() if isinstance(v, str)})
                TRANSLATIONS[_key] = _existing
except Exception:
    # 安全回退到内置常量
    pass
