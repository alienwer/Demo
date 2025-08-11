<!--
 * @Author: LK
 * @Date: 2025-08-08 20:40:15
 * @LastEditTime: 2025-08-09 05:44:52
 * @LastEditors: LK
 * @FilePath: /Demo/.trae/rules/project_rules.md
-->

## 一、技术栈与依赖管理

### 1. 核心框架版本

| 组件                 | 版本        | 依赖说明                   |
| -------------------- | ----------- | -------------------------- |
| **Flexiv RDK** | `>=1.6.0` | 需显式声明，默认版本 1.6.0 |

Environment Compatibility

| **OS**          | **Platform** | **C++ compiler kit** | **Python interpreter** |
| --------------------- | ------------------ | -------------------------- | ---------------------------- |
| Linux (Ubuntu 20.04+) | x86_64, aarch64    | GCC v9.4+                  | 3.8, 3.10, 3.12              |
| macOS 12+             | arm64              | Clang v14.0+               | 3.10, 3.12                   |
| Windows 10+           | x86_64             | MSVC v14.2+                | 3.8, 3.10, 3.12              |
| QNX 8.0.2+            | x86_64, aarch64    | QCC v12.2+                 | Not supported                |



- **使用conda环境**：在进行开发时，默认使用 `conda activate demo-env` 命令来激活开发环境，确保依赖与配置的一致性。
