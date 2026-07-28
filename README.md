# 🎮 Kerit-Renew
自动续期 Kerit 免费服务器，每 6 天定时成功运行（我这里为了保持成功，就做了每3天续期，做一次冗余预留）。

> ⚠️ Kerit 官网会对访问 IP 进行验证，GitHub Actions 的出口 IP 无法直接通过，因此必须配置代理。

## 🔐 Secrets 配置
**Settings → Secrets and variables → Actions → New repository secret** 添加以下变量：

| Secret 名 | 必填 | 说明 | 示例 |
|---|---|---|---|
| `KERIT_ACCOUNT` | ✅ 必填 | 🧾 Kerit 登录邮箱和 Gmail 应用密码，用英文逗号分隔 | `example@gmail.com,abcdabcdabcdabcd` |
| `HY2_PROXY_URL` | ✅ 必填 | 🌐 hy2 代理地址,代码里会自动由hy2生成一个临时的socks5，用完即刻销毁 | `hysteria2://[auth]@[host]:[port]/?sni=xxx&insecure=1&alpn=h3` |
| `TG_BOT` | 🔲 可选 | 📨 Telegram 推送，Chat ID 和 Bot Token 用英文逗号分隔 | `987654321,123456:AAFxxx` |
| `DISCORD_TOKEN` | 🔲 可选 | Discord Bot Token，用于向指定频道发送通知（Bot Token，不是用户 Token） | `Bot_xxx` |
| `DISCORD_CHANNEL` | 🔲 可选 | 目标频道 ID（整数字符串），例如 `123456789012345678` |

## 📝 Gmail 应用密码生成方式
Google 账号 → 安全性 → 两步验证（需先开启）→ 应用密码 → 选择"邮件" → 生成 → 将 16 位密码填入 Secret。

感谢以下大佬：

- https://github.com/losy-mify/Kerit-Renew
