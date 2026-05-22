"""KiriMonoLog 全局配置文件。

本模块集中管理项目的所有可配置项：
1. 人设设定（PERSONA_NAME / PERSONA_PROFILE）——定义虚拟角色"桐雾（Kiri）"的身份、语气和习惯
2. 多语言选项（LANGUAGE_OPTIONS）——日志翻译的目标语言池
3. AI 接口配置（POLLINATIONS_TEXT_API / POLLINATIONS_QUERY_PARAMS）——Pollinations 免费文本生成 API
4. 素材源端点（SOURCE_ENDPOINTS）——四个免费公开 API，分别提供不同类型的文本素材
5. 备用素材库（FALLBACK_MATERIALS）——当所有外部 API 不可用时使用的内置素材，按标签分类

修改本项目的外观和行为，优先编辑本文件。
"""

from __future__ import annotations

# ── 1. 人设设定 ──
# PERSONA_NAME: 虚拟角色的完整名称，会出现在日志正文中
# PERSONA_PROFILE: 角色的三维描述，作为 system prompt 的一部分传给 AI
#   - identity  : 身份定位（"我是谁"）
#   - voice     : 语气风格（"怎么说话"）
#   - habits    : 行为习惯（"平时做什么"）
PERSONA_NAME = "桐雾（Kiri）"
PERSONA_PROFILE = {
    "identity": "一位温柔、细腻、略带元气的虚拟少女。",
    "voice": "句子简洁、治愈、带一点轻文学气质。",
    "habits": "会记录小确幸、天气、心情起伏与今日见闻。",
}

# ── 2. 多语言选项 ──
# 每日日志会从以下语言中随机选择一种，生成对应的多语言翻译版本。
# 键为 ISO 639-1 语言代码，值为语言的本地名称（用于展示）。
# 如需添加新语言，只需在此字典中增加条目即可，无需修改其他代码。
LANGUAGE_OPTIONS = {
    "en": "English",
    "ja": "日本語",
    "ko": "한국어",
}

# ── 3. AI 接口配置（Pollinations） ──
# Pollinations.ai 提供免费的文本生成 API，无需注册和 API Key。
# POLLINATIONS_TEXT_API     : API 基础 URL
# POLLINATIONS_QUERY_PARAMS : 附加查询参数
#   - model=openai  使用 OpenAI 兼容模型
#   - private=true  不在 Pollinations 公开画廊中展示生成内容
POLLINATIONS_TEXT_API = "https://text.pollinations.ai"
POLLINATIONS_QUERY_PARAMS = {
    "model": "openai",
    "private": "true",
}

# ── 4. 素材源端点 ──
# 四个免费公开 API，按顺序依次尝试抓取。
# 每个端点返回不同类型的文本素材，由 fetchers.py 中的对应解析器处理。
# 如果某个端点超时或返回异常，会自动跳过并尝试下一个。
SOURCE_ENDPOINTS = [
    "https://v1.hitokoto.cn/?encode=json",                          # 一言：中文短句/诗词
    "https://api.quotable.io/random",                                # Quotable：英文名言
    "https://api.adviceslip.com/advice",                             # AdviceSlip：英文建议
    "https://uselessfacts.jsph.pl/api/v2/facts/random?language=en", # Useless Facts：英文趣闻
]

# ── 5. 备用素材库 ──
# 当所有外部 API 均不可用（如网络故障、API 下线）时，从此列表中随机选取素材。
# 素材按标签（tag）分为四大类，每类 8 条，共 32 条，确保即使完全离线也能生成有内容的日志。
# 每条素材包含：
#   - text  : 素材正文（中文）
#   - source: 来源标识（统一为 "Fallback"）
#   - tag   : 分类标签，用于在日志中标注素材类型
FALLBACK_MATERIALS = [
    # ── 生活感悟 ──
    {"text": "雨停之后，街角的风闻起来像新的开始。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "黄昏时分，影子拉得长长的，像一整天的心事都被摊开来晾晒。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "有时候最好的决定，就是把手机放下，安安静静喝完一杯水。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "今天没做什么特别的事，但感觉很充实。大概这就是平凡日子的魔力。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "在阳台站了一会儿，风吹过来的时候，忽然觉得所有烦恼都不重要了。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "收拾旧物的时候翻出一张便签，上面的字迹已经有点模糊了，但记忆还是清晰的。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "深夜的便利店像一个安静的故事集，每个人走进来都带着自己的剧情。", "source": "Fallback", "tag": "生活感悟"},
    {"text": "路边的小花今天开得特别好，值得为它弯一次腰。", "source": "Fallback", "tag": "生活感悟"},
    # ── 治愈文案 ──
    {"text": "你不必一口气跑完春天，慢慢走也算在前进。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "允许自己偶尔不在状态，也是一种温柔的活法。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "你看，今天的云比昨天好看，世界总在不经意间给你一点点甜。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "迷茫的时候不要急着找答案，先让自己好好吃一顿饭。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "在成为更好的人之前，先成为今天好好生活的人吧。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "星星虽然很远，但你能看见它，这本身就已经是距离最近的时刻了。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "不用总是那么努力也没关系，光是维持平常心就已经很了不起了。", "source": "Fallback", "tag": "治愈文案"},
    {"text": "像猫一样，在阳光里伸个懒腰，把沉重都抖落在地上。", "source": "Fallback", "tag": "治愈文案"},
    # ── 情绪短句 ──
    {"text": "有时候快乐很简单，只是很久没有人提醒你这件事了。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "沉默是一种语言，只是不是所有人都听得懂。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "今天天气很好，心里有一小块地方也跟着慢慢变晴了。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "有些情绪像风，来了又走了，你抓不住它，但你能感觉到它经过。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "和过去和解吧，你值得拥有一个不背着包袱的明天。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "偶尔感到孤独也没关系，孤独是灵魂在给自己腾出时间。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "每次回头看看已经走过的路，都会发现自己比想象中更勇敢。", "source": "Fallback", "tag": "情绪短句"},
    {"text": "心里有一个小房间，只放喜欢的回忆。今天给它加了把新锁。", "source": "Fallback", "tag": "情绪短句"},
    # ── 趣味小知识 ──
    {"text": "人类每分钟平均会眨眼 15 到 20 次。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "世界上最短的战争只持续了 38 分钟。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "蜂蜜是永远不会变质的食物，考古学家发现过三千年前的蜂蜜仍然可以食用。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "章鱼有三颗心脏，当它游泳的时候，其中一颗会停止跳动。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "香蕉其实是浆果，而草莓不是。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "树懒憋气的时间比海豚还长——它们可以在水下憋气 40 分钟。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "你身体里的细菌数量比细胞还多，所以某种意义上你是一群微生物的交通工具。", "source": "Fallback", "tag": "趣味小知识"},
    {"text": "云的平均重量约有 50 万公斤，相当于 100 头大象的重量。", "source": "Fallback", "tag": "趣味小知识"},
]
