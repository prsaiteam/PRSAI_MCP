# Prsai_Mcp
# PrsAi Staging MCP

提供两个 MCP 工具：

- `upload_file`：上传本地文件到 `https://prsai.cc/api/mcp/file/upload`
- `translate_ppt`：创建翻译任务 `https://prsai.cc/api/mcp/ppt/task/add`

`translate_ppt` 返回中会补充 `outppt_url`，格式为 `{base_url}/#/progress/{data}`（域名从 `PRS_AI_MCP_BASE_URL` 获取）。

## 使用前必读：注册并获取 API Key

`translate_ppt`（PPT 翻译）等 MCP 接口调用需要 `API Key` 鉴权。请先前往官网 https://prsai.cc/ 注册并登录，在个人中心/控制台申请 `API Key` 后再使用本 MCP。

官网首页（支持拖拽上传，支持 `.ppt/.pptx`，最大 100MB）：

[![PrsAi Staging 官网首页](./image.png)](https://prsai.cc/)
## 获取 API Key


使用前需要先在 PrsAi Staging 官网申请 `API Key`（用于调用 MCP 接口鉴权）：

1. 访问 https://prsai.cc/
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

## Trae 接入配置

在 Trae 的 MCP 配置中（点击设置 -> Workspace -> MCP，或直接编辑配置），添加如下 JSON 配置：

```json
{
  "mcpServers": {
    "prs-ai-staging-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/yanjiaqi/yanjiaqi/01-代码项目/MyCode/PrsAi_PPT_Translation_MCP/PrsAiStaging-MCP",
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

*注意：使用前请确保已安装 `uv`，并将 `--directory` 后的路径替换为您本地实际的 `PrsAiStaging-MCP` 绝对路径。*
