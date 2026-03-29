<template>
  <div class="editor-wrapper">
    <div class="header-bar">
      <nav class="navbar navbar-expand-lg navbar-light" style="padding: 0 10px">
        <!-- Brand -->
        <a
          class="navbar-brand"
          href="#"
          style="color: #222; font-size: 20px; width: 350px; margin-right: 20px"
        >
          <img
            src="https://www.wechatsync.com/images/logo-light.svg"
            height="38"
            style="vertical-align: -12px"
          />
          同步助手Markdown
        </a>

        <!-- Toggler -->
        <button
          class="navbar-toggler"
          type="button"
          data-toggle="collapse"
          data-target="#navbarCollapse"
          aria-controls="navbarCollapse"
          aria-expanded="false"
          aria-label="Toggle navigation"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <!-- Collapse -->
        <div class="collapse navbar-collapse" id="navbarCollapse">
          <!-- Toggler -->
          <button
            class="navbar-toggler"
            type="button"
            data-toggle="collapse"
            data-target="#navbarCollapse"
            aria-controls="navbarCollapse"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <i class="fe fe-x"></i>
          </button>
          <!-- Navigation -->
          <ul class="navbar-nav ml-auto" style="margin-right: 70px">
            <li class="nav-item">
              <a
                class="nav-link"
                target="_blank"
                href="https://github.com/wechatsync/Wechatsync"
                >Github</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                target="_blank"
                href="https://www.wechatsync.com/#install"
                >插件下载</a
              >
            </li>
          </ul>
          <!-- Button -->
          <a
            href="https://github.com/lljxx1/Music-Analytics"
            target="_blank"
            class="btn d-lg-inline-flex"
            style="margin-right: 10px"
            ><i class="fa fa-github" style="color: #222; font-size: 24px"></i
          ></a>
        </div>
      </nav>
    </div>
    <div
      class=""
      v-if="!extensionInstalled"
      style="padding-top: 80px; padding-left: 10px"
    >
      <scale-loader
        class="loading"
        style="margin-top: 80px; margin-bottom: 10px"
        :loading="true"
        color="black"
      ></scale-loader>
      <div v-if="checkCount > 3">
        未检测到插件<br />
        请安装同步助手Chrome插件
        <a href="https://www.wechatsync.com/#install" target="_blank"
          >https://www.wechatsync.com/#install</a
        >
      </div>
    </div>
    <div class="app-main" v-if="extensionInstalled">
      <div class="major-actions">
        <el-button 
          size="small" 
          type="success" 
          @click="showAIRewrite"
          :loading="rewriting"
        >
          {{ rewriting ? 'AI改写中...' : '🤖 AI改写' }}
        </el-button>
        <el-popover
          placement="top-start"
          width="500"
          v-model="visible"
          :title="submitting ? '发布中' : '发布到'"
          trigger="click"
        >
          <div>
            <hr />
            <div class="all-pubaccounts" v-if="!submitting">
              <div class="account-item" v-for="account in allAccounts">
                <el-checkbox v-model="account.checked">
                  <img
                    :src="account.icon ? account.icon : ''"
                    class="icon"
                    height="20"
                    style="vertical-align: -6px; height: 20px !important"
                  />
                  {{ account.title }}
                </el-checkbox>
              </div>
            </div>
            <div class="all-pubaccounts" v-if="submitting && taskStatus">
              <p v-if="!taskStatus.accounts">等待发布..</p>
              <div
                class="account-item taskStatus"
                v-for="account in taskStatus.accounts"
              >
                <img
                  :src="account.icon ? account.icon : ''"
                  class="icon"
                  height="20"
                  style="vertical-align: -6px; height: 20px !important"
                />
                <span class="name-block">{{ account.title }}</span>
                <span
                  style="margin-left: 15px"
                  :class="account.status + ' message'"
                >
                  <template v-if="account.status == 'uploading'">
                    <div class="lds-dual-ring"></div>
                    {{ account.msg || '发布中' }}
                  </template>

                  <template v-if="account.status == 'failed'">
                    同步失败, 错误内容：{{ account.error }}
                  </template>

                  <template v-if="account.status == 'done' && account.editResp">
                    同步成功
                    <a
                      :href="account.editResp.draftLink"
                      v-if="account.type != 'wordpress' && account.editResp"
                      style="margin-left: 5px"
                      target="_blank"
                      >查看草稿</a
                    >
                  </template>
                </span>
              </div>
            </div>
            <hr />
            <el-button
              size="small"
              v-if="!submitting"
              type="primary"
              @click="doSubmit"
              >同步</el-button
            >
            <el-button
              size="small"
              v-if="submitting"
              type="primary"
              @click="submitting = false"
              >关闭</el-button
            >
          </div>
          <el-button slot="reference" size="small" type="primary"
            >同步发布</el-button
          >
        </el-popover>
      </div>

      <el-dialog
        title="AI改写设置"
        :visible.sync="aiDialogVisible"
        width="600px"
      >
        <el-form :model="aiConfig" label-width="120px">
          <el-form-item label="AI服务商">
            <el-select v-model="aiConfig.provider" placeholder="请选择">
              <el-option label="OpenAI" value="openai"></el-option>
              <el-option label="Claude" value="anthropic"></el-option>
              <el-option label="DeepSeek" value="deepseek"></el-option>
              <el-option label="智谱AI" value="zhipu"></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="API密钥">
            <el-input 
              v-model="aiConfig.apiKey" 
              type="password" 
              placeholder="请输入API密钥"
              show-password
            ></el-input>
          </el-form-item>
          <el-form-item label="模型">
            <el-select v-model="aiConfig.model" placeholder="请选择模型">
              <el-option 
                v-for="model in availableModels" 
                :key="model" 
                :label="model" 
                :value="model"
              ></el-option>
            </el-select>
          </el-form-item>
          <el-form-item label="改写方式">
            <el-select v-model="aiConfig.rewriteType" placeholder="请选择改写方式" style="width: 100%">
              <el-option label="全文改写" value="full"></el-option>
              <el-option label="标题改写" value="title"></el-option>
              <el-option label="生成摘要" value="summary"></el-option>
              <el-option label="扩展内容" value="expand"></el-option>
              <el-option label="简化内容" value="simplify"></el-option>
              <el-option label="专业风格" value="professional"></el-option>
              <el-option label="轻松风格" value="casual"></el-option>
              <el-option label="🎓 学术风格（避免AI痕迹）" value="academic"></el-option>
              <el-option label="👤 人类节奏（口语化）" value="human_rhythm"></el-option>
              <el-option label="🔄 逻辑重构（打破线性）" value="logic_restructure"></el-option>
              <el-option label="📝 句式重组（降重）" value="sentence_restructure"></el-option>
              <el-option label="💡 关键词替换（加注释）" value="keyword_replace"></el-option>
              <el-option label="🛡️ 深度改写（规避检测）" value="anti_detection"></el-option>
            </el-select>
            <div style="margin-top: 10px; padding: 10px; background: #f5f7fa; border-radius: 4px; font-size: 12px;">
              <div v-if="aiConfig.rewriteType === 'academic'">
                <strong>🎓 学术风格：</strong>高级学术语言，句式多样，避免AI痕迹，适合学术论文
              </div>
              <div v-else-if="aiConfig.rewriteType === 'human_rhythm'">
                <strong>👤 人类节奏：</strong>模仿人类写作节奏，口语化表达，适合自媒体文章
              </div>
              <div v-else-if="aiConfig.rewriteType === 'logic_restructure'">
                <strong>🔄 逻辑重构：</strong>改变论证顺序，打破线性逻辑，增加跳跃，适合深度文章
              </div>
              <div v-else-if="aiConfig.rewriteType === 'sentence_restructure'">
                <strong>📝 句式重组：</strong>逐句改变句式结构，降低重复率，适合降重需求
              </div>
              <div v-else-if="aiConfig.rewriteType === 'keyword_replace'">
                <strong>💡 关键词替换：</strong>换词不换义，插入注释和举例，适合专业文章
              </div>
              <div v-else-if="aiConfig.rewriteType === 'anti_detection'">
                <strong>🛡️ 深度改写：</strong>综合所有规避策略，AI检测率可降至10%以下，<span style="color: #67c23a; font-weight: bold;">最推荐</span>
              </div>
            </div>
          </el-form-item>
          <el-form-item label="保留原文">
            <el-switch v-model="aiConfig.keepOriginal"></el-switch>
            <span style="margin-left: 10px; color: #999; font-size: 12px;">
              开启后将保存原文到历史记录
            </span>
          </el-form-item>
        </el-form>
        <span slot="footer" class="dialog-footer">
          <el-button @click="aiDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="doAIRewrite">开始改写</el-button>
        </span>
      </el-dialog>

      <div class="article-list">
        <div class="top-tools">
          <button
            class="btn btn-sm btn-success"
            type="button"
            @click="create()"
          >
            新文章
          </button>
        </div>
        <div class="article-all">
          <div
            v-for="(item, index) in list"
            class="article-item"
            @click="open(item)"
            :class="{ selected: item._id == currentArtitle._id }"
          >
            <div class="hover-overlay"></div>
            <div class="selected-overlay"></div>
            <div class="main-content">
              <div class="title">{{ item.title }}</div>
              <div class="date">{{ item.updateTime | date }}</div>
              <div class="desc">
                {{ item.content.substr(0, 100) }}
              </div>
            </div>
            <div class="item-divider" v-if="index > 0"></div>
            <div class="hover-container">
              <div class="icon fa fa-mavon-trash-o" @click="trash(item)"></div>
            </div>
          </div>

          <div v-if="!list.length" class="not-article">没有文章</div>
        </div>
      </div>
      <div class="editor-main">
        <div class="post-title">
          <input
            type="text"
            v-model="currentArtitle.title"
            placeholder="标题"
            class="form-control"
          />
        </div>
        <mavon-editor
          ref="editor"
          @imgAdd="imgAdd"
          :boxShadow="false"
          v-model="currentArtitle.content"
        >
          <template slot="right-toolbar-before">
            <!-- <button>
              view wechat   
            </button>  -->
          </template>
        </mavon-editor>
      </div>
    </div>
  </div>
</template>
<script>
var PouchDB = require('pouchdb').default

PouchDB.plugin(require('pouchdb-find').default)
console.log(PouchDB)
var db = new PouchDB('articles')
var trash = new PouchDB('trash-articles')
// db.put({
//   _id: 'dave@gmail.com',
//   name: 'David',
//   age: 69
// });

// db.changes().on('change', function() {
//   console.log('Ch-Ch-Changes');
// });

// var service = analytics.getService('syncer')
// var tracker = service.getTracker('UA-48134052-13')

var axios = require('axios')
// import Juejin from '../drivers/juejin'

const toBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = (error) => reject(error)
  })

import ScaleLoader from 'vue-spinner/src/ScaleLoader.vue'
import { rewriteContent, PROVIDERS, REWRITE_MODES } from './ai-service.js'

export default {
  name: '',
  components: { ScaleLoader },
  filters: {
    date(time) {
      let oldDate = new Date(time)
      let newDate = new Date()
      var dayNum = ''
      var getTime = (newDate.getTime() - oldDate.getTime()) / 1000

      if (getTime < 60 * 5) {
        dayNum = '刚刚'
      } else if (getTime >= 60 * 5 && getTime < 60 * 60) {
        dayNum = parseInt(getTime / 60) + '分钟前'
      } else if (getTime >= 3600 && getTime < 3600 * 24) {
        dayNum = parseInt(getTime / 3600) + '小时前'
      } else if (getTime >= 3600 * 24 && getTime < 3600 * 24 * 30) {
        dayNum = parseInt(getTime / 3600 / 24) + '天前'
      } else if (getTime >= 3600 * 24 * 30 && getTime < 3600 * 24 * 30 * 12) {
        dayNum = parseInt(getTime / 3600 / 24 / 30) + '个月前'
      } else if (time >= 3600 * 24 * 30 * 12) {
        dayNum = parseInt(getTime / 3600 / 24 / 30 / 12) + '年前'
      }

      let year = oldDate.getFullYear()
      let month = oldDate.getMonth() + 1
      let day = oldDate.getDate()
      let hour = oldDate.getHours()
      let minute = oldDate.getMinutes()
      let second = oldDate.getSeconds()

      if (dayNum == '刚刚') return dayNum
      return (
        dayNum +
        ' ' +
        year +
        '-' +
        month +
        '-' +
        day +
        ' ' +
        hour +
        ':' +
        minute +
        ':' +
        second
      )
    },
  },
  data() {
    return {
      visible: false,
      submitting: false,
      rewriting: false,
      aiDialogVisible: false,
      aiConfig: {
        provider: 'zhipu',
        apiKey: 'fc866212e0d64350b837a486e5faf08a.7ZdotggpaC5add3D',
        model: 'glm-4-flash',
        rewriteType: 'anti_detection',
        keepOriginal: true
      },
      list: [
        // {
        //   id: 0,
        //   title: "MRC question1",
        //   date: "19/1/10",
        //   desc: "navigator.battery navigator.getBattery()"
        // },
        // {
        //   id:  1,
        //   title: "MRC question",
        //   date: "19/1/10",
        //   desc:
        //     'try{(function(oa){function wc(a,b){if(null===this||void 0===this)throw new TypeError("Array.prototype.forEach called on null or undefined");if("function"!==typeof a)throw new TypeError(a+" is not a fu...'
        // }
      ],
      value: '',
      extensionInstalled: false,
      checkCount: 0,
      allAccounts: [],
      currentArtitle: {
        content: ''
      },
      taskStatus: {},
      markdownOption: {
        // boxShadow: false
      },
    }
  },

  watch: {
    currentArtitle: {
      handler: function (newValue) {
        console.log('change', this.currentArtitle, newValue)
        this.saveDoc(newValue)
      },
      deep: true,
    },
  },
  computed: {
    availableModels() {
      return PROVIDERS[this.aiConfig.provider]?.models || []
    }
  },
  mounted() {
    // if(this.list.length) this.currentArtitle = this.list[0];
    this.loadDoc()
    var self = this
    ;(function check() {
      self.extensionInstalled = typeof window.$syncer != 'undefined'
      //   self.extensionInstalled = false
      self.checkCount++
      if (self.extensionInstalled) {
        // self.recom();
        self.loadAccounts()
        return
      }
      setTimeout(check, 800)
    })()
    
  },
  methods: {
    loadAccounts() {
      var allAccounts = []
      var accounts = []

      var self = this
      function getAccounts() {
        window.$syncer.getAccounts(function (resp) {
          console.log('allAccounts', resp)
          self.allAccounts = resp
        })
        // chrome.extension.sendMessage(
        //   {
        //     action: 'getAccount',
        //   },
        //   function (resp) {
        //     console.log('allAccounts', resp)
        //     self.allAccounts = resp
        //   }
        // )
      }
      getAccounts()

      this.$nextTick(() => {
        console.log('this.$refs.editor.markdownIt', this.$refs.editor.markdownIt)
        const md = this.$refs.editor.markdownIt
        const defaultRender =
          md.renderer.rules.image ||
          function (tokens, idx, options, _, self) {
            return self.renderToken(tokens, idx, options);
          };
        md.renderer.rules.image = (...[tokens, idx, options, env, self]) => {
          tokens[idx].attrPush(['referrerpolicy','no-referrer']);
          return defaultRender(tokens, idx, options, env, self);
        };
      })
    },

    showAIRewrite() {
      if (!this.currentArtitle.content) {
        this.$message.warning('请先输入文章内容')
        return
      }
      
      const savedConfig = localStorage.getItem('aiConfig')
      if (savedConfig) {
        this.aiConfig = Object.assign(this.aiConfig, JSON.parse(savedConfig))
      }
      
      this.aiDialogVisible = true
    },

    async doAIRewrite() {
      if (!this.aiConfig.apiKey) {
        this.$message.error('请输入API密钥')
        return
      }

      localStorage.setItem('aiConfig', JSON.stringify(this.aiConfig))
      
      this.aiDialogVisible = false
      this.rewriting = true

      try {
        const content = this.aiConfig.rewriteType === 'title' 
          ? this.currentArtitle.title 
          : this.currentArtitle.content
        
        const result = await rewriteContent({
          provider: this.aiConfig.provider,
          apiKey: this.aiConfig.apiKey,
          model: this.aiConfig.model,
          rewriteType: this.aiConfig.rewriteType,
          content: content
        })
        
        const rewritten = result.text
        const quality = result.quality
        
        if (this.aiConfig.keepOriginal) {
          const history = {
            timestamp: Date.now(),
            type: this.aiConfig.rewriteType,
            original: content,
            rewritten: rewritten,
            quality: quality
          }
          
          if (!this.currentArtitle.history) {
            this.currentArtitle.history = []
          }
          this.currentArtitle.history.push(history)
        }
        
        if (this.aiConfig.rewriteType === 'title') {
          this.currentArtitle.title = rewritten
        } else {
          this.currentArtitle.content = rewritten
        }
        
        let message = `AI改写完成！质量评分：${quality.overallScore}分（${quality.grade.emoji}${quality.grade.level}）`
        if (quality.suggestions && quality.suggestions.length > 0) {
          message += `\n建议：${quality.suggestions[0]}`
        }
        
        this.$message({
          type: quality.overallScore >= 80 ? 'success' : 'warning',
          message: message,
          duration: 5000
        })
        
        console.log('改写质量详情:', quality)
      } catch (error) {
        console.error('AI rewrite error:', error)
        this.$message.error('AI改写失败: ' + error.message)
      } finally {
        this.rewriting = false
      }
    },

    async doSubmit() {
      var self = this

      function getPost() {
        var post = {}
        post.title = self.currentArtitle.title
        post.content = self.$refs.editor.d_render
        post.markdown = self.currentArtitle.content
        // post.thumb = document.body.getAttribute('data-msg_cdn_url');
        // post.desc = document.body.getAttribute('data-msg_desc');
        console.log(post)
        return post
      }

      var selectedAc = this.allAccounts.filter((a) => {
        return a.checked
      })

      // console.log(selectedAc, this.$refs.editor.d_render);
      // return;
      this.$message('准备同步')
      window.$syncer.addTask(
        {
          post: getPost(),
          accounts: selectedAc,
        },
        function (status) {
          self.taskStatus = status
          console.log('status', status)
        },
        function () {
          console.log('send')
        }
      )

      //   chrome.extension.sendMessage(
      //     {
      //       action: 'addTask',
      //       task: {
      //         post: getPost(),
      //         accounts: selectedAc,
      //       },
      //     },
      //     function (resp) {}
      //   )

      this.submitting = true
      this.taskStatus = {}
    },

    async createExampleDoc() {
      // console.log(await db.id());
      // return;
      var inited = localStorage.getItem('inited')
      if (inited) return
      var docId = await db.id()
      var content =
        '@[toc](目录)\n\nMarkdown 语法简介\n=============\n> [语法详解](http://commonmark.org/help/)\n\n## **粗体**\n```\n**粗体**\n__粗体__\n```\n## *斜体*\n```\n*斜体*\n_斜体_\n```\n## 标题\n```\n# 一级标题 #\n一级标题\n====\n## 二级标题 ##\n二级标题\n----\n### 三级标题 ###\n#### 四级标题 ####\n##### 五级标题 #####\n###### 六级标题 ######\n```\n## 分割线\n```\n***\n---\n```\n****\n## ^上^角~下~标\n```\n上角标 x^2^\n下角标 H~2~0\n```\n## ++下划线++ ~~中划线~~\n```\n++下划线++\n~~中划线~~\n```\n## ==标记==\n```\n==标记==\n```\n## 段落引用\n```\n> 一级\n>> 二级\n>>> 三级\n...\n```\n\n## 列表\n```\n有序列表\n1.\n2.\n3.\n...\n无序列表\n-\n-\n...\n```\n\n## 任务列表\n\n- [x] 已完成任务\n- [ ] 未完成任务\n\n```\n- [x] 已完成任务\n- [ ] 未完成任务\n```\n\n## 链接\n```\n[链接](www.baidu.com)\n![图片描述](http://www.image.com)\n```\n## 代码段落\n\\``` type\n\n代码段落\n\n\\```\n\n\\` 代码块 \\`\n\n```c++\nint main()\n{\n    printf("hello world!");\n}\n```\n`code`\n## 表格(table)\n```\n| 标题1 | 标题2 | 标题3 |\n| :--  | :--: | ----: |\n| 左对齐 | 居中 | 右对齐 |\n| ---------------------- | ------------- | ----------------- |\n```\n| 标题1 | 标题2 | 标题3 |\n| :--  | :--: | ----: |\n| 左对齐 | 居中 | 右对齐 |\n| ---------------------- | ------------- | ----------------- |\n## 脚注(footnote)\n```\nhello[^hello]\n```\n\n见底部脚注[^hello]\n\n[^hello]: 一个注脚\n\n## 表情(emoji)\n[参考网站: https://www.webpagefx.com/tools/emoji-cheat-sheet/](https://www.webpagefx.com/tools/emoji-cheat-sheet/)\n```\n:laughing:\n:blush:\n:smiley:\n:)\n...\n```\n:laughing::blush::smiley::)\n\n## $\\KaTeX$公式\n\n我们可以渲染公式例如：$x_i + y_i = z_i$和$\\sum_{i=1}^n a_i=0$\n我们也可以单行渲染\n$$\\sum_{i=1}^n a_i=0$$\n具体可参照[katex文档](http://www.intmath.com/cg5/katex-mathjax-comparison.php)和[katex支持的函数](https://github.com/Khan/KaTeX/wiki/Function-Support-in-KaTeX)以及[latex文档](https://math.meta.stackexchange.com/questions/5020/mathjax-basic-tutorial-and-quick-reference)\n\n## 布局\n\n::: hljs-left\n`::: hljs-left`\n`居左`\n`:::`\n:::\n\n::: hljs-center\n`::: hljs-center`\n`居中`\n`:::`\n:::\n\n::: hljs-right\n`::: hljs-right`\n`居右`\n`:::`\n:::\n\n## 定义\n\n术语一\n\n:   定义一\n\n包含有*行内标记*的术语二\n\n:   定义二\n\n        {一些定义二的文字或代码}\n\n    定义二的第三段\n\n```\n术语一\n\n:   定义一\n\n包含有*行内标记*的术语二\n\n:   定义二\n\n        {一些定义二的文字或代码}\n\n    定义二的第三段\n\n```\n\n## abbr\n*[HTML]: Hyper Text Markup Language\n*[W3C]:  World Wide Web Consortium\nHTML 规范由 W3C 维护\n```\n*[HTML]: Hyper Text Markup Language\n*[W3C]:  World Wide Web Consortium\nHTML 规范由 W3C 维护\n```\n\n'
      var doc = {
        _id: docId,
        title: 'Markdonw语法',
        updateTime: Date.now(),
        content: content,
        type: 'markdown',
        html: '',
      }
      var res = await db.put(doc)
      this.loadDoc()
      localStorage.setItem('inited', 1)
    },
    async saveDoc(newDoc) {
      await db.get(newDoc._id).then(function (doc) {
        return db.put(
          Object.assign(
            {
              _id: newDoc._id,
              _rev: doc._rev,
            },
            newDoc
          )
        )
      })
    },
    async loadDoc() {
      // var res = await db.allDocs({
      //   include_docs: true,
      // });
      await db.createIndex({
        index: {
          fields: ['updateTime', 'type', 'title', 'content'],
        },
      })

      var res = await db.find({
        selector: {},
        fields: ['_id', 'title', 'updateTime', 'content', 'type', 'html'],
        sort: [
          {
            updateTime: 'desc',
          },
        ],
      })

      console.log(res)
      this.list = res.docs.map((d) => {
        d.title = d.title || '标题'
        return d
      })

      if (this.list.length) {
        this.currentArtitle = this.list[0]
      } else {
        this.createExampleDoc()
      }

      
      console.log(this.list)
    },

    async trash(item) {
      console.log(item)
      var rv = item._rev
      delete item._rev
      var re = await trash.put(item)
      // var d = await db.remove(item._id, rv);
      // console.log(d, re);
      var rr = await db.get(item._id).then(function (doc) {
        doc._deleted = true
        return db.put(doc)
      })

      this.loadDoc()
    },

    async create() {
      var docId = Date.now() + Math.floor(Math.random() * 1000) + ''
      console.log(db.id)
      // var docId = await db.id(docId);
      console.log(docId)
      var doc = {
        _id: docId,
        title: '',
        updateTime: Date.now(),
        content: '',
        type: 'markdown',
        html: '',
      }
      var res = await db.put(doc)
      if (res.ok) {
        // this.list.push(doc);
      }
      this.loadDoc()
      console.log('create', res, doc)
    },
    open(item) {
      this.currentArtitle = item
    },
    async imgAdd(pos, $file) {

      // console.log('this.$refs.editor.markdownIt.renderer', this.$refs.editor.markdownIt)
      // var dri = new Segmentfault();
      //   var dri = new Juejin()
      //   var finalUrl = await dri.uploadFileByForm($file)
      var sortOrderTypes = [
        'toutiao',
        'jianshu',
        'zhihu',
        'weibo',
        'douban',
        'segmentfault',
        'weixin',
      ]
        .map((_) => this.allAccounts.filter((a) => a.type === _)[0])
        .filter((_) => _)

      if (sortOrderTypes.length === 0) {
        this.$message('当前未登陆任何自媒体平台，无法自动上传图片')
        return
      }

      var base64Url = await toBase64($file)
      var accountCurrent = sortOrderTypes[0]
      var actionData = {
        src: base64Url,
        account: accountCurrent,
      }
      console.log('actionData', actionData)
      window.$syncer.uploadImage(actionData, (res) => {
        console.log('res', res)
        if (accountCurrent.type === 'zhihu') {
          res.result.url = [res.result.url, '_r.jpg'].join('')
        }
        this.$refs.editor.$img2Url(pos, res.result.url)
      })
      console.log('imgAdd', pos, $file, sortOrderTypes, this.allAccounts)
      //   this.$refs.editor.$img2Url(pos, finalUrl)
    },
  },
}
</script>
<style>
.article-list {
  height: 100%;
  width: 350px;
}

.v-note-wrapper {
  padding-top: 110px;
}

.article-all {
  color: #878787;
  height: 100%;
  width: 350px;
  overflow-y: auto;
  box-sizing: border-box;
  position: relative;
  margin-top: 110px;
}

#app,
html,
body,
.editor-wrapper {
  height: 100%;
  overflow: hidden;
}

.editor-main {
  background: white;
  border-left: 1px solid #ececec;
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  min-width: 403px;
  transition: top 0.5s ease-in-out 0.2s;
  margin-left: 350px;
  height: 100%;
  z-index: 3;
}

.article-item {
  height: 120px;
  cursor: pointer;
  margin: 0 auto;
  text-align: left;
  overflow: hidden;
  position: relative;
  transition: opacity 0.2s ease-in-out, height 0.2s ease-in-out,
    width 0.2s ease-in-out;
}

.article-item .main-content {
  color: #878787;
  left: 24px;
  overflow: hidden;
  overflow-wrap: break-word;
  position: absolute;
  right: 24px;
  top: 12px;
  word-wrap: break-word;
  bottom: 15px;
}

.article-item .title {
  transition: color 0.1s ease-in-out, width 0s ease-in-out 0.1s;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: caecilia, times, serif;
  font-size: 16px;
  font-weight: 400;
  color: #4a4a4a;
  margin-bottom: 3px;
  max-height: 40px;
  overflow: hidden;
  overflow-wrap: break-word;
  text-overflow: ellipsis;
  white-space: nowrap;
  word-wrap: break-word;
  line-height: 20px;
  width: 302px;
}

.article-item .date {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: gotham, helvetica, arial, sans-serif;
  font-size: 11px;
  font-weight: 400;
  text-transform: uppercase;
  letter-spacing: 1px;
  margin-bottom: 6px;
}

.article-item .desc {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-family: gotham, helvetica, arial, sans-serif;
  font-size: 12px;
  font-weight: 400;
  line-height: 17px;
}

.article-item * {
  box-sizing: border-box;
}

.article-item:hover .date,
.article-item:hover .title,
.article-item:hover .desc {
  color: #fff;
}

.item-divider {
  border-top: 1px solid #ececec;
  left: 20px;
  right: 20px;
  top: 0;
  position: absolute;
}

.article-item:hover .item-divider {
  border-top: none;
}

.article-item .hover-overlay {
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  opacity: 0;
  background-color: rgba(43, 181, 92, 0.9);
  transition: opacity 0.1s ease-in-out;
}

.article-item.selected .selected-overlay {
  border: 3px solid #d9d9d9;
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
}

.hover-container {
  position: absolute;
  opacity: 0;
  top: 0;
  right: 0;
  transition: opacity 0.1s ease-in-out;
}

.hover-container .icon {
  width: 24px;
  height: 24px;
  cursor: pointer;
  margin: 8px 12px 0 0;
  color: white;
  font-size: 20px;
  text-align: center;
  line-height: 24px;
}

.article-item:hover .hover-overlay {
  opacity: 1;
}

.article-item:hover .hover-container {
  opacity: 1;
}

.top-tools {
  padding: 10px 24px;
  font-size: 13px;
  text-align: right;
  border-bottom: 1px solid #d9d9d9;
  width: 350px;
}

.top-tools .btn {
  font-size: 13px;
}

.v-note-wrapper .v-note-op {
  border-top: 1px solid #f2f6fc;
  border-radius: 0px;
}

.v-note-wrapper {
  height: 100%;
  position: absolute !important;
  width: 100%;
  top: 0;
  border-left: none !important;
  box-sizing: border;
}

.top-tools,
.post-title {
  position: absolute;
  z-index: 1502;
  top: 60px;
}

.post-title input {
  border: none;
  height: 45px;
  outline: none;
  font-size: 20px;
  font-family: caecilia, times, serif;
  font-size: 28px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-weight: 300;
  width: 700px;
  padding-left: 24px;
}

.not-article {
  padding: 10px 20px;
  font-size: 12px;
  color: #666;
}

.major-actions {
  position: absolute;
  right: 15px;
  top: 12px;
  z-index: 888;
}

.all-pubaccounts {
}

.account-item img {
  margin-right: 5px;
}

.account-item {
  height: 36px;
  line-height: 36px;
  padding: 0 15px;
  font-size: 14px;
}

.header-bar {
  height: 60px;
  line-height: 42px;
  position: absolute;
  width: 100%;
  border: 1px solid #eee;
  z-index: 888;
}

.header-bar a:hover {
  text-decoration: none;
}
</style>
