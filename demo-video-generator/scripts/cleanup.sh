#!/bin/bash
# 项目清理脚本 - 删除冗余文件
# 执行前请确认已备份重要文件

echo "🧹 开始清理冗余文件..."
echo ""

# 1. 删除迭代报告文档
echo "📄 删除迭代报告文档..."
rm -f AESTHETIC-OPTIMIZATION-REPORT.md
rm -f CODE-BASED-THUMBNAIL-ANALYSIS-v1.3.0.md
rm -f CODE-REVIEW-REPORT-v1.1.0.md
rm -f COMPLETE-ITERATION-SUMMARY-v1.1.0.md
rm -f CONTINUOUS-LEARNING-AND-ITERATION-v1.1.0.md
rm -f DESIGN-RESEARCH-REPORT-2025.md
rm -f DESIGN-SPEC-CHECK-REPORT.md
rm -f EMOJI-GENERATION-SOLUTION-v3.0.0.md
rm -f EMOJI-UPGRADE-REPORT-v3.0.0.md
rm -f EVOLUTION-ROADMAP-v2.0.0.md
rm -f FINAL-COMPLETION-REPORT-v1.1.0.md
rm -f FINAL-DESIGN-CHECK-REPORT.md
rm -f FINAL-VALIDATION-REPORT-v1.1.0.md
rm -f ITERATION-COMPLETION-REPORT-v1.1.0.md
rm -f ITERATION-COMPLETION-REPORT-v1.2.0.md
rm -f ITERATION-COMPLETION-SUMMARY-v1.1.0.md
rm -f ITERATION-PLAN-v1.1.0.md
rm -f OPTIMIZATION-IMPLEMENTATION-REPORT-v1.2.0.md
rm -f OPTIMIZATION-PLAN-v1.2.0.md
rm -f OPTIMIZATION-SUMMARY-v1.2.0.md
rm -f PROJECT-SNAPSHOT-v1.1.0.md
rm -f QUALITY-CHECK-REPORT.md
rm -f SELF-EVALUATION-AND-ITERATION-v1.1.0.md
rm -f TEST-AND-OPTIMIZATION-SUMMARY-v1.1.0.md
rm -f THUMBNAIL-ANALYSIS-AND-IMPROVEMENT-v1.3.0.md
rm -f THUMBNAIL-CODE-REVIEW-v1.3.0.md
rm -f THUMBNAIL-DEEP-ANALYSIS-v2.0.0.md
rm -f THUMBNAIL-GENERATOR-DESIGN-v1.3.0.md
rm -f THUMBNAIL-IMPLEMENTATION-REPORT-v1.3.0.md
rm -f THUMBNAIL-IMPROVEMENT-REPORT-v1.4.0.md
rm -f THUMBNAIL-INTEGRATION-REPORT-v1.3.0.md
rm -f THUMBNAIL-OPTIMIZATION-GUIDE.md
rm -f THUMBNAIL-UPGRADE-REPORT-v2.0.0.md
rm -f V4-CODE-REVIEW-REPORT.md
rm -f V4-UPGRADE-SUMMARY.md
echo "✅ 已删除 35 个迭代报告文档"
echo ""

# 2. 删除冗余文档
echo "📄 删除冗余文档..."
rm -f CSS-EXPRESSIVE-FACES-GUIDE.md
rm -f MRBEAST-DESIGN-ANALYSIS.md
rm -f docs/SHOCKED-TEMPLATE-GUIDE.md
echo "✅ 已删除 3 个冗余文档"
echo ""

# 3. 可选：删除辅助脚本 (如果只做封面生成)
read -p "是否删除辅助脚本（视频生成、配音等）？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🗑️  删除辅助脚本..."
    rm -f lib/demo_video_generator.py
    rm -f lib/emoji_generator.py
    rm -f lib/enhanced_subtitle_generator.py
    rm -f lib/format_combiner.py
    rm -f lib/parallel_voiceover_generator.py
    rm -f lib/prompt_optimizer.py
    rm -f lib/video_recorder.py
    echo "✅ 已删除 7 个辅助脚本"
fi
echo ""

# 4. 可选：删除冗余示例
read -p "是否删除冗余示例脚本？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🗑️  删除冗余示例..."
    rm -f examples/test_expressive_faces.py
    rm -f examples/test_mrbeast_style.py
    rm -f examples/test_optimized_templates.py
    rm -f examples/thumbnail_optimization_examples.py
    rm -f examples/v4_viral_marketing.py
    rm -f examples/vertical_thumbnail_examples.py
    rm -f examples/advanced_thumbnail_test.py
    rm -f examples/full_design_check.py
    echo "✅ 已删除 8 个冗余示例"
fi
echo ""

# 5. 可选：删除冗余测试
read -p "是否删除冗余测试文件？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "🗑️  删除冗余测试..."
    rm -f tests/test_emoji_template.py
    rm -f tests/test_shocked_template.py
    rm -f tests/test_demo_video_generator.py
    rm -f tests/test_integration.py
    echo "✅ 已删除 4 个冗余测试"
fi
echo ""

echo "🎉 清理完成！"
echo ""
echo "📊 清理统计:"
echo "   - 已删除迭代报告: 35个"
echo "   - 已删除冗余文档: 3个"
echo ""
echo "📁 保留的核心文件:"
echo "   - 核心脚本: 6个"
echo "   - 核心模板: 53个"
echo "   - 核心文档: 4个"
echo "   - 核心示例: 4个"
echo "   - 总计: 67个核心文件"
