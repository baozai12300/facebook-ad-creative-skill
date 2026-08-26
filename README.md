# Facebook Ad Creative Skill

一个面向 Facebook / Meta 广告图文创意生成的开源 Skill 项目，重点服务电商与消费品营销场景。

这个项目不是单一 Prompt，而是一套可复用的广告创意生成工作流：通过受众、卖点角度、场景、视觉风格、版式和批量变体策略，帮助 AI 助手为同一个产品生成多方向、可测试、适合移动端广告投放的图文创意方案。

## 适用场景

- Facebook / Meta Feed 广告图
- Story / Reels 封面创意
- ASC / Advantage+ Shopping Campaign 素材池探索
- 电商产品图文广告批量测试
- 消费品、家居、美妆、宠物、服饰、电子产品、礼品、健康类产品创意生成

## 项目结构

```text
facebook-ad-creative-skill/
├── .claude/skills/facebook-ad-creative/
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   │   └── compile_creatives.py
│   └── references/
│       ├── engines/
│       │   ├── audience-engine.md
│       │   ├── angle-engine.md
│       │   ├── layout-engine.md
│       │   ├── scene-style-engine.md
│       │   └── variation-strategy.md
│       ├── templates/
│       │   ├── input.schema.json
│       │   ├── creative-output.schema.json
│       │   └── prompt-templates.json
│       └── examples/
│           └── product-inputs.json
├── data/
│   └── sample-products.json
├── docs/
│   ├── design-philosophy.md
│   ├── model-adapters.md
│   └── open-source-guide.md
├── examples/
│   ├── beauty-serum.json
│   ├── pet-bed.json
│   └── demo-output.json
├── generated-images/
│   └── .gitkeep
├── LICENSE
└── README.md
```

## 快速使用

在支持 Skills 的 AI 编程环境中，把仓库中的 `.claude/skills/facebook-ad-creative` 放到对应的 skills 目录。

也可以直接运行脚本，把产品输入编译成广告创意计划和图片模型 Prompt：

```bash
python .claude/skills/facebook-ad-creative/scripts/compile_creatives.py examples/beauty-serum.json
```

输出内容包含：

- Creative Plan：受众、兴趣词、痛点、卖点、场景、风格、版式、文案方向、差异点
- Model Prompt：通用 Prompt、GPT Image 2 优化版、Nano Banana 优化版、负面约束
- Batch Diversity Notes：同批次差异化说明

## 输入示例

```json
{
  "product_name": "GlowBarrier Vitamin C Serum",
  "product_category": "beauty skincare",
  "product_description": "A lightweight vitamin C serum for dull skin, uneven tone, and daily glow.",
  "key_features": ["10% vitamin C", "hyaluronic acid", "non-sticky texture"],
  "benefits": ["brighter-looking skin", "more even tone", "hydrated finish"],
  "target_audiences": ["busy professionals", "skincare beginners"],
  "audience_location": "United States",
  "price_positioning": "mid-range",
  "brand_tone": "clean, confident, modern",
  "platform": "facebook",
  "aspect_ratio": "4:5",
  "language": "en",
  "generation_count": 6,
  "campaign_goal": "purchase",
  "awareness_stage": "cold",
  "text_overlay_mode": "light",
  "variation_strength": "high"
}
```

## 核心能力

- Audience Engine：受众切片、兴趣词、购买动机、认知阶段
- Angle Engine：痛点解决、结果导向、UGC、对比、社会证明、礼赠、优惠等角度
- Scene Engine：家居、通勤、办公室、户外、厨房、礼赠、Studio 等场景
- Style Engine：UGC 真实感、高转化广告风、Premium、极简电商、信息图等风格
- Layout Engine：ASC V1、Social Proof、Problem Solution、Comparison、Review Card 等版式
- Variation Strategy：批量生成时控制受众、场景、风格、版式、文案语气、色彩气质和镜头语言差异
- Model Adapters：分别输出 GPT Image 2 与 Nano Banana 适配 Prompt

## 重要说明

本项目不会承诺“保证跑赢算法”。它采用更专业、可信的方式：通过多创意角度、多受众假设、多场景表达、多视觉信号和结构化变量测试，提高广告素材池的探索广度，让 Meta 广告系统更容易获得可区分的创意信号。

## License

MIT
