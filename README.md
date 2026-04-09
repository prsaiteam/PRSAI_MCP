# PPT Translator Agent

专业级、由大模型驱动的 PPTX 翻译 Agent，具备“约束感知”的文本拟合能力：在翻译演示文稿的同时，尽量保持原有格式、版式与视觉一致性。

## 为什么优于通用大模型

通用大模型产品（Claude Code、Gemini、GPT、Manus、豆包等）也能翻译 PPTX，但往往缺少对“格式与版式约束”的精细控制。本 Agent 面向高保真结果做了专门优化：

- **语义级格式保持** —— 按“语义”做映射而非按“位置”。跨语言词序变化时，粗体、颜色、重点标注仍尽量落在正确的词上。
- **约束感知文本拟合** —— 基于真实文本框边界估算可用字符预算，结合不同文字体系的宽度比例，并通过多轮迭代处理溢出。
- **复杂对象支持** —— 支持翻译图形、表格、图表等内部文本，而不只限于形状/文本框。
- **RTL 自动对齐** —— 在希伯来语、阿拉伯语等从右到左语言互译时，自动调整文字方向与对齐方式。
- **第三方插件支持** —— 对 think-cell 等元素（智能图表对象）提供部分支持。

提供两个 MCP 工具：

- `upload_file`：上传本地文件到 `https://prsai.cc/api/mcp/file/upload`
- `translate_ppt`：创建翻译任务 `https://prsai.cc/api/mcp/ppt/task/add`

`translate_ppt` 返回中会补充 `outppt_url`，格式为 `{base_url}/#/progress/{data}`（域名从 `PRS_AI_MCP_BASE_URL` 获取）。

## 使用前必读：注册并获取 API Key

`translate_ppt`（PPT 翻译）等 MCP 接口调用需要 `API Key` 鉴权。请先前往官网 https://prsai.cc/ 注册并登录，在个人中心/控制台申请 `API Key` 后再使用本 MCP。

官网首页（支持拖拽上传，支持 `.ppt/.pptx`，最大 100MB）：

<a href="https://prsai.cc/"><img src="./assets/home.png" alt="PrsAi PPT 翻译 MCP 官网首页" width="720"></a>

## 翻译效果对比

翻译前/翻译后对比图展示效果：

| 翻译前（中文）                                            | 翻译后（英文）                                           |
| -------------------------------------------------- | ------------------------------------------------- |
| ![翻译前（中文）](./assets/translation-before.png) | ![翻译后（英文）](./assets/translation-after.png) |

说明：

- 目标是尽量保持原 PPT 的版式、字体、配色、图表与重点标注样式不变
- 适用于需要“格式保持 + 批量翻译”的 PPT 场景，减少手工排版调整成本

## 获取 API Key

使用前需要先在 PrsAi Staging 官网申请 `API Key`（用于调用 MCP 接口鉴权）：

1. 访问 <https://prsai.cc/>
2. 注册并登录账号
3. 进入个人中心/控制台，申请并复制 `API Key`

拿到 `API Key` 后，你可以：

- 配置环境变量 `PRS_AI_MCP_API_KEY`
- 或在每次调用 MCP 工具时通过入参 `api_key` 传入

## 配置

可选环境变量：

- `PRS_AI_MCP_API_KEY`：默认 api_key（等价于接口参数 `mcpToken`）
- `PRS_AI_MCP_BASE_URL`：默认 `https://prsai.cc`

`PRS_AI_MCP_API_KEY` 的读取顺序：tool 入参 `api_key` → 环境变量 `PRS_AI_MCP_API_KEY` → 项目根目录 `.env`。

即使不配置环境变量，也可以在每次调用 tool 时传入 `api_key`。

## 本地运行

在该目录安装依赖后运行：

```bash
python -m prs_ai_staging_mcp
```

或使用脚本入口：

```bash
prs-ai-staging-mcp
```

## 第三方接入（Trae / OpenClaw / Codex / ClaudeCode / Coze）

本项目提供的是 MCP Server。只要第三方工具支持 MCP（stdio 方式启动本地进程），就可以按同一套参数接入：

- **command**：`uv`
- **args**：`["--directory", "/absolute/path/to/Prsai_Mcp/PPT-Translation-MCP", "run", "prs-ai-staging-mcp"]`
- **env**：`PRS_AI_MCP_API_KEY`（必填）、`PRS_AI_MCP_BASE_URL=https://prsai.cc`（可选）

## Trae 接入配置

在 Trae 的 MCP 配置中（点击设置 -> Workspace -> MCP，或直接编辑配置），添加如下 JSON 配置：

```json
{
  "mcpServers": {
    "prs-ai-staging-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/Prsai_Mcp/PPT-Translation-MCP",
        "run",
        "prs-ai-staging-mcp"
      ],
      "env": {
        "PRS_AI_MCP_API_KEY": "请替换为您的真实API_KEY",
        "PRS_AI_MCP_BASE_URL": "https://prsai.cc"
      }
    }
  }
}
```

## OpenClaw 接入配置

在 OpenClaw 的「工具 / 插件 / MCP Servers」新增一个自定义 MCP Server（stdio），填入上面的 command/args/env 即可；或者将github项目地址直接丢给 OpenClaw，由 OpenClaw 自动拉取项目代码，安装依赖。

OpenClaw 配置示例：

```json
{
  "mcpServers": {
    "prs-ai-staging-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/Prsai_Mcp/PPT-Translation-MCP",
        "run",
        "prs-ai-staging-mcp"
      ],
      "env": {
        "PRS_AI_MCP_API_KEY": "请替换为您的真实API_KEY",
        "PRS_AI_MCP_BASE_URL": "https://prsai.cc"
      }
    }
  }
}
```


## Codex 接入配置

Codex 支持通过 CLI 添加 MCP Server，或直接编辑 `~/.codex/config.toml`（或项目内 `.codex/config.toml`）。你可以按下述方式添加一个 stdio Server：

```bash
codex mcp add prsai-ppt-translation \
  --command uv \
  --args --directory /absolute/path/to/Prsai_Mcp/PPT-Translation-MCP run prs-ai-staging-mcp \
  --env PRS_AI_MCP_API_KEY=你的API_KEY \
  --env PRS_AI_MCP_BASE_URL=https://prsai.cc
```

## ClaudeCode 接入配置

在 ClaudeCode 的 MCP Servers 配置中新增一个 stdio Server（字段名通常也是 `mcpServers`），command/args/env 与 Trae 配置保持一致即可：

```json
{
  "mcpServers": {
    "prsai-ppt-translation": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/Prsai_Mcp/PPT-Translation-MCP",
        "run",
        "prs-ai-staging-mcp"
      ],
      "env": {
        "PRS_AI_MCP_API_KEY": "你的API_KEY",
        "PRS_AI_MCP_BASE_URL": "https://prsai.cc"
      }
    }
  }
}
```

## Coze 接入配置

如果你使用的是 Coze 工作流/插件的 HTTP 调用方式（而不是 MCP），也可以直接请求对应接口：

- 上传文件：`POST https://prsai.cc/api/mcp/file/upload`（multipart/form-data：`file` + `mcpToken`）
- 创建翻译任务：`POST https://prsai.cc/api/mcp/ppt/task/add`

```json
{
  "translateLanguage": "en",
  "pptUrl": "上传后返回的URL",
  "mcpToken": "你的API_KEY",
  "fileOriginalName": "demo.pptx"
}
```

*注意：使用前请确保已安装* *`uv`，并将* *`--directory`* *后的路径替换为您本地实际的* *`PPT-Translation-MCP`* *绝对路径。*
