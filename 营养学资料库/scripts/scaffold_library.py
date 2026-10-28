#!/usr/bin/env python3
"""生成营养学资料库的目录骨架：模块导读、总目录、data/nav.json。

只负责"骨架"，不写具体知识内容。重复运行会覆盖自动生成的导读与目录，
但不会删除任何已存在的文章文件。
"""

import json
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent.parent
UPDATED = "2026-10-23"
FORCE = "--force" in sys.argv

MODULES = [
    {
        "id": "basics",
        "dir": "01-营养学基础",
        "title": "营养学基础",
        "icon": "🧬",
        "position": "建立学科坐标系：营养学解决什么问题、人体如何处理食物、能量如何被消耗、营养素需求如何被标准化。",
        "outcome": "能说清必需营养素、消化吸收路径、能量消耗的四个组成部分，以及 DRIs 各指标的含义与用途。",
        "related": ["02-宏量营养素", "03-微量营养素", "10-营养评估与干预"],
        "refs": ["《营养与食品卫生学》", "《现代营养学》", "中国营养学会 DRIs", "WHO/FAO 能量与蛋白质需求报告"],
        "topics": [
            ("营养学概论", "introduction", "营养学研究的对象、边界，以及它与医学、食品科学的关系是什么？"),
            ("消化、吸收与代谢", "digestion-absorption", "食物从入口到被细胞利用，经过哪些环节，哪些环节决定营养吸收效率？"),
            ("能量代谢与消耗", "energy-metabolism", "基础代谢、食物热效应、日常活动和运动各占多少，如何测量与估算？"),
            ("营养素分类与 DRIs", "nutrient-classification", "必需营养素如何分类，EAR、RNI、AI、UL、AMDR 分别怎么用？"),
        ],
    },
    {
        "id": "macronutrients",
        "dir": "02-宏量营养素",
        "title": "宏量营养素",
        "icon": "🍚",
        "position": "把蛋白质、碳水、脂类、纤维和水讲透：它们是什么、怎么代谢、吃多少、吃错了会怎样。",
        "outcome": "能判断一种食物的宏量营养构成，能按体重和活动量估算蛋白质与热量需求，能解释 GI、氨基酸评分等常用指标。",
        "related": ["01-营养学基础", "06-能量平衡与体重管理", "08-运动营养"],
        "refs": ["《中国居民膳食指南（2022）》", "FAO/WHO 蛋白质与脂肪酸报告", "《中国食物成分表（标准版）》"],
        "topics": [
            ("蛋白质", "protein", "优质蛋白怎么定义，动物蛋白与植物蛋白如何搭配，不同人群需要多少？"),
            ("碳水化合物", "carbohydrate", "糖、淀粉、膳食纤维如何区分，GI 和 GL 该怎么用，代糖能不能替代糖？"),
            ("脂类", "lipids", "饱和、单不饱和、多不饱和、反式脂肪有什么区别，omega-3 与 omega-6 该如何平衡？"),
            ("膳食纤维", "dietary-fiber", "可溶与不可溶纤维作用有何不同，为什么推荐 25~30 克，吃多了有什么风险？"),
            ("水与电解质", "water-electrolytes", "每天该喝多少水，钠钾平衡如何影响血压，出汗后该怎么补？"),
        ],
    },
    {
        "id": "micronutrients",
        "dir": "03-微量营养素",
        "title": "微量营养素",
        "icon": "💊",
        "position": "逐个梳理维生素与矿物质：功能、食物来源、缺乏表现、过量风险与检测边界。",
        "outcome": "能根据饮食结构判断潜在缺乏风险，能读懂常见检测指标，能区分“食补优先”和“必须补充”的场景。",
        "related": ["02-宏量营养素", "07-生命周期营养", "09-疾病营养", "11-补剂与功能食品"],
        "refs": ["中国营养学会 DRIs", "《中国居民膳食指南（2022）》", "WHO 微量营养素指南", "《中国食物成分表（标准版）》"],
        "topics": [
            ("维生素总论", "vitamins-overview", "维生素如何分类，哪些容易缺乏，补充剂和食物来源有什么差别？"),
            ("脂溶性维生素 A/D/E/K", "fat-soluble-vitamins", "四种脂溶性维生素各自管什么，缺乏和过量分别有什么表现？"),
            ("水溶性维生素 B 族/C", "water-soluble-vitamins", "B 族和维生素 C 如何参与能量代谢，烹饪损失有多大？"),
            ("常量元素：钙磷镁钠钾氯", "major-minerals", "钙镁钾为什么和骨骼、血压、肌肉功能都有关，摄入比例重要吗？"),
            ("微量元素：铁锌碘硒等", "trace-minerals", "铁、锌、碘、硒缺乏如何识别，谁最需要关注，过量有什么风险？"),
            ("植物化学物", "phytochemicals", "多酚、类胡萝卜素、硫化物有什么作用，证据强度到哪里为止？"),
        ],
    },
    {
        "id": "foods",
        "dir": "04-食物与食品",
        "title": "食物与食品",
        "icon": "🥦",
        "position": "从“营养素”回到“餐桌上的食物”：各类食物的营养特点、加工与烹饪带来的变化，以及如何看标签和判断安全。",
        "outcome": "能按食物类别快速判断营养密度，能识别超加工食品，能独立读懂配料表、营养成分表和执行标准。",
        "related": ["02-宏量营养素", "03-微量营养素", "05-膳食模式与指南", "13-实操工具"],
        "refs": ["《中国居民膳食指南（2022）》", "《中国食物成分表（标准版）》", "GB 28050 预包装食品营养标签通则", "NOVA 食品分类"],
        "topics": [
            ("食物分类与营养特点", "food-groups", "谷薯、蔬果、畜禽鱼蛋、奶豆坚果、油盐各自提供什么，怎么快速判断营养密度？"),
            ("食品加工与营养变化", "food-processing", "精制、发酵、腌制、冷冻、罐装分别损失什么，什么是超加工食品？"),
            ("烹饪与营养保留", "cooking-nutrition", "蒸煮炒炸烤对维生素和蛋白质有什么影响，怎样减少营养损失和有害产物？"),
            ("食品标签与选购", "food-labeling", "配料表、营养成分表、营养声称和执行标准怎么读，哪些是营销话术？"),
            ("食品安全与添加剂", "food-safety-additives", "微生物、农残、重金属和食品添加剂的风险边界在哪里，怎么降低日常风险？"),
        ],
    },
    {
        "id": "dietary-patterns",
        "dir": "05-膳食模式与指南",
        "title": "膳食模式与指南",
        "icon": "🍽️",
        "position": "从单一营养素上升到整体饮食结构：中国居民膳食指南、地中海饮食、DASH、素食模式的结构与证据。",
        "outcome": "能对比不同膳食模式的共同点与差异，能把指南条目翻译成一日三餐的具体选择。",
        "related": ["04-食物与食品", "06-能量平衡与体重管理", "09-疾病营养"],
        "refs": ["《中国居民膳食指南（2022）》", "WHO 健康饮食建议", "DASH 临床试验文献", "地中海饮食相关队列研究"],
        "topics": [
            ("中国居民膳食指南（2022）", "chinese-dietary-guidelines", "八条准则和平衡膳食宝塔分别解决什么问题，怎么落到日常？"),
            ("地中海饮食", "mediterranean-diet", "它的核心结构是什么，有哪些证据支持，如何适配中国饮食？"),
            ("DASH 饮食", "dash-diet", "DASH 为什么能降压，具体吃什么、限制什么，执行难点在哪？"),
            ("素食与弹性素食", "vegetarian-diets", "素食有哪些类型，最容易缺哪些营养素，如何科学搭配？"),
        ],
    },
    {
        "id": "weight",
        "dir": "06-能量平衡与体重管理",
        "title": "能量平衡与体重管理",
        "icon": "⚖️",
        "position": "把能量平衡讲成可执行的体重管理方案：减重、增肌、维持、防反弹，以及行为与心理因素。",
        "outcome": "能估算个人热量需求，能设计温和可持续的减重或增肌方案，能识别平台期、暴食循环和伪科学方法。",
        "related": ["02-宏量营养素", "05-膳食模式与指南", "08-运动营养", "10-营养评估与干预"],
        "refs": ["《中国居民膳食指南（2022）》", "《成人肥胖食养指南》", "WHO 肥胖管理建议", "能量平衡与代谢适应相关研究"],
        "topics": [
            ("能量平衡原理", "energy-balance", "摄入与消耗如何共同决定体重变化，为什么体重不是线性下降？"),
            ("减重策略", "weight-loss", "热量缺口开多大、蛋白质吃多少、要不要运动，平台期怎么处理？"),
            ("增肌与增重", "muscle-gain", "增重期热量盈余多少合适，蛋白质如何分配，如何避免只长脂肪？"),
            ("体重维持与防反弹", "weight-maintenance", "减重后代谢会发生什么变化，哪些习惯最能预测长期维持成功？"),
            ("进食行为与心理", "eating-behavior", "情绪性进食、暴食和节食循环如何形成，行为改变有哪些可用工具？"),
        ],
    },
    {
        "id": "lifecycle",
        "dir": "07-生命周期营养",
        "title": "生命周期营养",
        "icon": "👶",
        "position": "按人生阶段梳理营养需求变化：备孕孕期、婴幼儿、儿童青少年、成年、老年。",
        "outcome": "能说出各阶段的关键营养素与常见风险，能为家庭成员做针对性的饮食调整。",
        "related": ["03-微量营养素", "06-能量平衡与体重管理", "09-疾病营养"],
        "refs": ["《中国居民膳食指南（2022）》", "中国营养学会妇幼营养指南", "WHO 婴幼儿喂养建议", "老年肌少症共识"],
        "topics": [
            ("备孕、孕期与哺乳期", "pregnancy-lactation", "叶酸、铁、钙、DHA 该怎么补，孕期体重增长多少合适，哪些食物要避免？"),
            ("婴幼儿喂养", "infancy", "母乳与配方奶如何选择，辅食何时加、怎么加，如何预防过敏？"),
            ("儿童与青少年", "children-adolescents", "生长突增期需要什么，挑食和肥胖如何干预，骨骼健康怎么打底？"),
            ("成年期营养", "adulthood", "久坐、外食、应酬为主的成年人，如何守住营养底线？"),
            ("老年营养", "older-adults", "蛋白质、维生素 D、B12 为什么关键，肌少症、吞咽困难和食欲下降怎么应对？"),
        ],
    },
    {
        "id": "sports",
        "dir": "08-运动营养",
        "title": "运动营养",
        "icon": "🏃",
        "position": "运动场景下的能量与底物利用、训练前后补给、增肌减脂营养策略，以及常见运动补剂的证据。",
        "outcome": "能按运动类型和时长安排碳水与蛋白质，能判断运动饮料和补剂是否必要。",
        "related": ["02-宏量营养素", "06-能量平衡与体重管理", "11-补剂与功能食品"],
        "refs": ["ACSM 运动营养立场声明", "ISSN 运动营养指南", "《中国居民膳食指南（2022）》"],
        "topics": [
            ("运动能量代谢", "exercise-metabolism", "磷酸原、糖酵解、有氧氧化分别支撑什么强度的运动，脂肪何时成为主供能？"),
            ("运动前中后补给", "pre-post-workout", "练前吃什么、练中要不要补糖、练后多久补蛋白，补水怎么安排？"),
            ("增肌与减脂期营养", "body-recomposition", "热量盈余或缺口下，蛋白质、碳水、脂肪如何分配，如何减少肌肉流失？"),
            ("水、电解质与运动补剂", "hydration-supplements", "运动饮料、咖啡因、肌酸、乳清蛋白，哪些有证据、哪些是智商税？"),
        ],
    },
    {
        "id": "clinical",
        "dir": "09-疾病营养",
        "title": "疾病营养",
        "icon": "🏥",
        "position": "常见慢性病与消化系统疾病的医学营养治疗原则：机制、饮食调整、证据与就医边界。",
        "outcome": "能理解疾病饮食处方的逻辑，能识别需要转诊的信号，不把科普内容当成个体化医疗建议。",
        "related": ["05-膳食模式与指南", "07-生命周期营养", "10-营养评估与干预"],
        "refs": ["中国糖尿病医学营养治疗指南", "中国血脂管理指南", "KDIGO 营养建议", "中国痛风诊疗指南", "ESPEN 指南"],
        "topics": [
            ("超重与肥胖", "obesity", "肥胖如何评估，生活方式干预、药物和手术的边界在哪里？"),
            ("糖尿病与胰岛素抵抗", "diabetes", "碳水质量、进食顺序、餐后血糖和体重管理如何配合？"),
            ("血脂异常与心血管疾病", "dyslipidemia-cvd", "脂肪质量、膳食纤维、植物甾醇各自能起多大作用？"),
            ("高血压与钠钾平衡", "hypertension", "限盐能降多少血压，DASH 和补钾如何执行？"),
            ("高尿酸与痛风", "gout", "嘌呤、果糖、酒精和饮水分别怎么影响尿酸，急性期怎么吃？"),
            ("慢性肾脏病", "ckd", "不同分期蛋白质、钠、钾、磷如何调整，什么时候需要限制？"),
            ("肝脏、胆囊与胰腺疾病", "liver-gallbladder-pancreas", "脂肪肝、肝硬化、胆囊炎、胰腺炎的饮食重点有何不同？"),
            ("胃肠道疾病", "gi-diseases", "反流、胃炎、炎症性肠病、肠易激综合征和便秘腹泻怎么吃？"),
            ("肿瘤与肌少症", "cancer-sarcopenia", "治疗期如何保证能量和蛋白质，恶病质与肌肉流失如何干预？"),
        ],
    },
    {
        "id": "assessment",
        "dir": "10-营养评估与干预",
        "title": "营养评估与干预",
        "icon": "📋",
        "position": "营养工作的方法论：怎么调查饮食、怎么测量身体、怎么看指标、怎么下诊断和做随访。",
        "outcome": "能完成一次基础膳食评估，能读懂 BMI、腰围、体脂和常见生化指标，能写出可执行的目标与随访计划。",
        "related": ["01-营养学基础", "09-疾病营养", "13-实操工具"],
        "refs": ["《中国居民膳食指南（2022）》", "中国营养学会注册营养师教材", "ESPEN 营养筛查与评估指南"],
        "topics": [
            ("膳食调查方法", "dietary-assessment", "24 小时回顾、食物频率问卷、称重法和记录法各适合什么场景，误差从哪来？"),
            ("人体测量与体格指标", "anthropometry", "BMI、腰围、腰臀比、体脂率和皮褶厚度怎么测、怎么解读？"),
            ("生化与临床评估", "biochemical-clinical", "血常规、白蛋白、血脂、血糖和微量元素指标能说明什么，不能说明什么？"),
            ("营养诊断与方案制定", "nutrition-diagnosis", "如何从评估结果形成营养诊断，设定目标并安排随访？"),
            ("营养咨询与行为改变", "nutrition-counseling", "动机访谈、SMART 目标和依从性管理怎么用在饮食调整上？"),
        ],
    },
    {
        "id": "supplements",
        "dir": "11-补剂与功能食品",
        "title": "补剂与功能食品",
        "icon": "🧴",
        "position": "补剂不是“多多益善”：讲清法规、常见产品证据、适用人群、剂量与风险。",
        "outcome": "能判断某类补剂是否有必要、证据是否充分，能识别虚假宣传和剂量风险。",
        "related": ["03-微量营养素", "08-运动营养", "12-循证营养与辟谣"],
        "refs": ["中国保健食品法规", "NIH ODS 补剂事实表", "USP 第三方认证", "Cochrane 补剂系统评价"],
        "topics": [
            ("膳食补充剂总论", "supplement-overview", "补剂和食物的关系是什么，哪些人群确实需要补充？"),
            ("常见补剂证据盘点", "supplement-evidence", "维生素 D、钙、鱼油、蛋白粉、益生菌、复合维生素、胶原蛋白的证据分别如何？"),
            ("保健食品与法规", "health-food-regulation", "蓝帽子是什么，功能声称和广告合规边界在哪里？"),
            ("补剂选购与风险", "supplement-safety", "怎么看第三方检测、剂量、相互作用和过量风险？"),
        ],
    },
    {
        "id": "evidence",
        "dir": "12-循证营养与辟谣",
        "title": "循证营养与辟谣",
        "icon": "🔬",
        "position": "营养信息噪声极大，这一模块教你判断研究质量、读懂争议、识别营销话术。",
        "outcome": "能区分相关性研究与因果证据，能识别单一研究放大、剂量偷换和利益冲突，能快速查证一个营养说法。",
        "related": ["01-营养学基础", "11-补剂与功能食品", "14-专题"],
        "refs": ["GRADE 证据分级", "Cochrane Handbook", "WHO/FAO 技术报告", "PubMed / Cochrane Library"],
        "topics": [
            ("研究设计与证据等级", "study-design-evidence", "RCT、队列、病例对照、横断面和系统评价各能回答什么问题？"),
            ("营养学常见争议", "nutrition-controversies", "饱和脂肪、胆固醇、碳水、盐、红肉、有机食品的争议到底卡在哪？"),
            ("谣言识别方法论", "misinformation-method", "如何识别单一研究、剂量误导、相关当因果和断章取义？"),
            ("信息源与数据库", "information-sources", "哪些指南、数据库和期刊值得优先信任，怎么查原始文献？"),
        ],
    },
    {
        "id": "tools",
        "dir": "13-实操工具",
        "title": "实操工具",
        "icon": "🛠️",
        "position": "把知识变成动作：食物成分表、份量估算、食谱编制、饮食记录与清单模板。",
        "outcome": "能独立查食物成分、估算份量、编一天食谱，并用记录工具做复盘。",
        "related": ["02-宏量营养素", "06-能量平衡与体重管理", "10-营养评估与干预"],
        "refs": ["《中国食物成分表（标准版）》", "《中国居民膳食指南（2022）》", "USDA FoodData Central"],
        "topics": [
            ("食物成分表使用", "food-composition-table", "怎么查能量和营养素，可食部、生熟比和烹调损失怎么处理？"),
            ("份量与食物交换份", "portion-exchange", "手掌法、碗盘法和食物交换份如何互相换算？"),
            ("食谱编制", "menu-planning", "如何按目标热量和三大营养素比例编一日三餐？"),
            ("饮食记录与热量计算", "dietary-records", "称重、估算和 App 记录各有什么误差，怎么坚持？"),
        ],
    },
    {
        "id": "topics",
        "dir": "14-专题",
        "title": "专题",
        "icon": "🧩",
        "position": "跨模块的前沿与热点：肠道菌群、时间营养、精准营养、食物环境与可持续饮食。",
        "outcome": "能区分这些领域的确定结论、初步证据和商业炒作。",
        "related": ["03-微量营养素", "05-膳食模式与指南", "12-循证营养与辟谣"],
        "refs": ["Nature/Science 相关综述", "ISAPP 益生菌共识", "FAO 可持续饮食报告", "中国居民膳食指南（2022）"],
        "topics": [
            ("肠道菌群与益生菌", "gut-microbiota", "菌群如何影响健康，益生菌、益生元、后生元的证据分别到什么程度？"),
            ("时间营养学", "chrononutrition", "生物钟如何影响代谢，进食窗口、早餐和夜宵该怎么安排？"),
            ("精准营养与基因", "precision-nutrition", "基因多态性和微生物组检测能否指导个人饮食，边界在哪里？"),
            ("食物环境与可持续饮食", "sustainable-diets", "超加工食品、外卖环境和食物浪费如何影响健康与选择？"),
        ],
    },
]


def module_slug(module):
    return module["dir"].split("-", 1)[1]


def write_module_guide(module):
    folder = LIB / module["dir"]
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "00-模块导读.md"
    if target.exists() and not FORCE:
        return
    rel = module["related"]
    lines = [
        "---",
        f'title: "{module["title"]}｜模块导读"',
        f'slug: "guide-{module["id"]}"',
        f'module: "{module["title"]}"',
        "order: 0",
        'status: "active"',
        f"updated: {UPDATED}",
        "---",
        "",
        f"# {module['icon']} {module['title']}｜模块导读",
        "",
        "## 模块定位",
        "",
        module["position"],
        "",
        "## 学完能做到",
        "",
        module["outcome"],
        "",
        "## 主题清单",
        "",
        "| # | 主题 | 核心问题 | 状态 |",
        "|---|---|---|---|",
    ]
    for index, (title, slug, question) in enumerate(module["topics"], start=1):
        lines.append(f"| {index:02d} | **{title}** | {question} | ⬜ 待补充 |")
    lines += [
        "",
        "## 与其他模块的关系",
        "",
    ]
    for item in rel:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 建议参考",
        "",
    ]
    for item in module["refs"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## 写作约定",
        "",
        "1. 每个主题单独成文，文件名用两位序号 + 上表中的主题名，例如 `01-主题名.md`；标题含 `/` 时用 `-` 代替",
        "2. 文章开头写 frontmatter：title、slug、module、order、status、tags、summary、updated",
        "3. 结构统一为：核心结论 → 关键概念 → 数据与证据 → 常见误区 → 实操建议 → 参考来源",
        "4. 数字必须能追溯到指南、教材或原始文献；没有出处的经验性说法标注为“待核实”",
        "5. 写完后把本表中的 ⬜ 改为 ✅，并同步 `data/nav.json` 的 status 与 file 字段",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def write_overview():
    folder = LIB / "00-总览"
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "00-总目录.md"
    if target.exists() and not FORCE:
        return
    total = sum(len(m["topics"]) for m in MODULES)
    lines = [
        "---",
        'title: "总目录"',
        'slug: "master-index"',
        'module: "总览"',
        "order: 1",
        'status: "active"',
        f"updated: {UPDATED}",
        "---",
        "",
        "# 总目录",
        "",
        f"共 **{len(MODULES)} 个模块、{total} 个主题**。当前为骨架阶段，标 ⬜ 的主题待补充内容。",
        "",
        "| 模块 | 主题数 | 解决什么问题 | 入口 |",
        "|---|---|---|---|",
    ]
    total = 0
    for module in MODULES:
        count = len(module["topics"])
        total += count
        lines.append(
            f"| {module['icon']} **{module['title']}** | {count} | {module['position']} | [导读](../{module['dir']}/00-模块导读.md) |"
        )
    lines += [
        "",
        f"合计：**{total} 个主题**。",
        "",
        "## 按问题找内容",
        "",
        "| 你想解决 | 先去 |",
        "|---|---|",
        "| 不知道从哪学起 | [学习路径](01-学习路径.md) |",
        "| 看不懂营养名词 | [术语表](02-术语表.md) |",
        "| 想减重 / 增肌 | 06 能量平衡与体重管理 |",
        "| 想给父母调整饮食 | 07 生命周期营养 → 老年营养 |",
        "| 体检查出指标异常 | 09 疾病营养（并就医） |",
        "| 想辨别保健品和谣言 | 11 补剂与功能食品 + 12 循证营养与辟谣 |",
        "| 想马上照着做 | 13 实操工具 |",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def write_nav():
    data = {
        "site": {
            "title": "营养学资料库",
            "subtitle": "系统化、可扩展、循证的营养知识体系",
            "version": "1.0.0",
            "stage": "content-draft-complete",
            "updated": UPDATED,
            "contentRoot": "营养学资料库",
            "outputRoot": "营养学资料库/pages",
        },
        "theme": {
            "style": "textbook-modern",
            "primary": "#1F5C4A",
            "accent": "#C97B3D",
            "background": "#FBFAF6",
            "layout": "sidebar + content + toc",
            "features": ["模块导航", "主题检索", "学习路径", "状态标记", "上一篇/下一篇", "术语悬浮解释"],
        },
        "modules": [],
    }
    target = LIB / "data" / "nav.json"
    existing = {}
    if target.exists():
        old_nav = json.loads(target.read_text(encoding="utf-8"))
        for old_module in old_nav.get("modules", []):
            for old_topic in old_module.get("topics", []):
                existing[old_topic["slug"]] = {
                    "status": old_topic.get("status", "planned"),
                    "file": old_topic.get("file"),
                }

    for index, module in enumerate(MODULES, start=1):
        topics = []
        for order, (title, slug, question) in enumerate(module["topics"], start=1):
            previous = existing.get(slug, {})
            topic = {
                "title": title,
                "slug": slug,
                "order": order,
                "status": previous.get("status", "planned"),
                "coreQuestion": question,
                "plannedPath": f"{module['dir']}/{order:02d}-{title.replace('/', '-')}.md",
            }
            if previous.get("file"):
                topic["file"] = previous["file"]
            topics.append(topic)
        data["modules"].append(
            {
                "id": module["id"],
                "dir": module["dir"],
                "title": module["title"],
                "icon": module["icon"],
                "order": index,
                "guide": f"{module['dir']}/00-模块导读.md",
                "position": module["position"],
                "outcome": module["outcome"],
                "related": module["related"],
                "topics": topics,
            }
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_template():
    folder = LIB / "_模板"
    folder.mkdir(parents=True, exist_ok=True)
    text = """---
title: "文章标题"
slug: "article-slug"
module: "所属模块"
order: 1
status: "draft"
tags: [标签1, 标签2]
summary: "一句话说明这篇解决什么问题"
updated: 2026-10-23
---

# 文章标题

## 核心结论

用 3~5 句话给出可执行的结论，先给答案再展开。

## 关键概念

| 概念 | 解释 | 常见误解 |
|---|---|---|
|  |  |  |

## 数据与证据

- 数据点 1（来源：）
- 数据点 2（来源：）

## 常见误区

1. 误区描述 → 纠正
2. 误区描述 → 纠正

## 实操建议

1. 
2. 
3. 

## 参考来源

- 《中国居民膳食指南（2022）》
- 
"""
    (folder / "文章模板.md").write_text(text, encoding="utf-8")


def main():
    LIB.mkdir(parents=True, exist_ok=True)
    for module in MODULES:
        write_module_guide(module)
    write_overview()
    write_nav()
    write_template()
    for extra in ["pages", "assets/css", "assets/js", "assets/images"]:
        (LIB / extra).mkdir(parents=True, exist_ok=True)
    (LIB / "pages" / ".gitkeep").touch()
    total = sum(len(m["topics"]) for m in MODULES)
    print(f"生成完成：{len(MODULES)} 个模块，{total} 个主题。")


if __name__ == "__main__":
    main()
