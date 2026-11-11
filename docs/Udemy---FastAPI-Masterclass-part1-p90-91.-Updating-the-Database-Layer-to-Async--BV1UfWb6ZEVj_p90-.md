

# 🚀 FastAPI 大师课：第90-91节：将数据库层升级为异步


在本节课中我们将要学习如何把 FastAPI 应用的数据库层从同步升级为异步。整个改造会围绕数据库连接字符串、异步引擎、异步建表函数、异步会话依赖和路由层收到的会话类型展开，目标是把原来会阻塞的数据库操作改成不会阻塞事件循环的异步操作。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_1.png)

> 这节课的核心改造可以用一句话概括：把同步的 `engine`、`Session` 和 `create_all` 换成异步版本，同时保持路由层的依赖注入方式基本不变。

把 FastAPI 应用改成异步代码的第一步，是更新数据库设置。不过在正式进入数据库改造之前，需要先打开 `pyproject.toml` 文件，这个文件负责配置项目依赖。你在课程开始执行 `uv sync` 时，这些依赖已经下载到项目里了。这里需要特别指出，`aiosqlite` 这个异步 I/O SQLite 库才是真正让 SQLite 支持异步连接的库。目前数据库和所有会话都是同步的、会阻塞的，接下来要把它们升级或重构为异步。下面先看依赖和连接字符串中需要确认的几个点。

- `pyproject.toml` 管理项目依赖，`uv sync` 已经把这些依赖安装到项目环境中。

- `aiosqlite` 提供 SQLite 的异步支持，是把 SQLite 连接升级为异步连接的关键依赖。

- 当前数据库连接和会话仍然是同步阻塞的，后续要统一改成异步。

- 改造入口是 `database.py` 文件，先从这里调整数据库连接字符串和引擎。

依赖确认完之后，现在转到 `database.py` 文件。有一段时间没有进入这个文件了，这次从 SQLite URL 字符串开始修改。标准 SQLite 方式是同步的，这个字符串配置的是到数据库的连接。下面先看数据库 URL 的结构和改造方式。

```text
数据库 URL 结构 = 方言 + 驱动://...
```

原字符串的第一部分是 `sqlite`，这部分叫方言，用来配置实际数据库类型；如果以后想换成 PostgreSQL 或 MySQL，就可以换掉这一部分。在 `sqlite` 后面、冒号前面，需要加上加号并写 `aiosqlite`。加号后面的第二部分叫驱动，用来配置或定制数据库连接。这样仍然使用 SQLite，只是指定 `aiosqlite` 实现，以便用异步方式使用 SQLite。

```python
# 原来：同步 SQLite
sqlite:///./database.db

# 现在：异步 SQLite
sqlite+aiosqlite:///./database.db
```

这个模式适用于任何数据库。例如使用 PostgreSQL 时，常规异步连接字符串会写成 `postgresql`，再配合 `asyncpg` 库配置成 `postgresql+asyncpg`。本质上就是通过加号把前一个数据库配置和另一个驱动库组合起来，其余逻辑完全相同。

```python
# PostgreSQL 的异步连接示例
postgresql+asyncpg://user:password@localhost/dbname
```

连接字符串确认之后，下一个改动是把 `create_engine` 替换为配套的 `create_async_engine` 函数。录制时 SQLModel 还没有直接导出这个函数，所以需要从 SQLModel 底层依赖的 SQLAlchemy ORM 中导入。新版本可能会改变导出位置，但目前可以从 SQLAlchemy 的 `ext.asyncio` 包导入，同时不再需要 `create_engine`，因此要删除原来的导入。下面列出引擎替换中需要注意的导入和参数变化。

- 从 `sqlalchemy.ext.asyncio` 导入 `create_async_engine`。

- 删除不再需要的 `create_engine` 导入。

- 把创建引擎的调用改成 `create_async_engine`。

- 删除原来的 `connect_args` 参数，因为异步模式下不需要这段同步世界的效率优化代码。

- 删除 SQLite 同步代码专用的线程设置，因为异步事件循环本质上在单线程上切换任务，不再需要那套跨线程共享连接的限制规避方案。

导入和引擎创建可以写成下面这样。

```python
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./database.db")
```

之前代码里的 `connect_args` 用来定制数据库连接，在同步世界里是为了争取一些效率。现在有了异步能力，这段代码基本不需要了，可以直接删除。之前那段线程设置是 SQLite 针对同步代码的特殊 workaround：SQLite 默认模块不允许连接跨线程共享，而异步代码实际上在单个线程上运行，因为异步事件循环会在不同操作之间切换，所以这个限制和优化都不再需要担心，可以把设置选项移除。

引擎替换完成后，下一个要更新的是 `create_db_and_tables` 函数。这个函数运行在 FastAPI 应用实例化的 lifespan 中。这里的 `create_all` 函数实际上是同步的，不支持传入异步引擎，所以需要更新这个函数。这段代码来自 SQLModel 和 SQLAlchemy 的等效异步文档设置，这种设置跟着教程做一次，基本在应用生命周期内都够用；底层细节如果一时觉得困惑，不必担心，它在现实中属于一次性操作。

第一步是把函数改成异步函数，也就是加上 `async` 关键字。上一课讲过，函数加 `async` 后，如果没有可等待、可暂停的操作，加这个关键字没有意义，因为线程无法在函数体内做别的事情。下面先看异步建表函数的结构。

```python
async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
```

在函数体内要创建异步上下文管理器。上下文管理器就是使用 Python 的 `with` 关键字，后面跟着创建某种对象，`with` 负责释放或清理这个对象。例如在 Python 中创建文件时，可以用这种语法确保文件写入后被关闭。这里对异步引擎调用 `begin()` 方法，它会授予一个连接对象的访问权，这个连接对象表示到数据库的连接。用 `as` 给连接命名，社区惯例是 `conn`，也就是 connection 的缩写。

`begin()` 返回的是异步上下文管理器，类似于普通上下文管理器，但为异步操作做了优化。因此要在 `with` 前面再加 `async` 关键字。最后，函数体内必须使用 `await` 来等待可等待操作，这里对连接对象调用 `run_sync` 方法。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_3.png)

![](img/86754ea2b9a04286ccbb50af3bc3a46e_4.png)

```python
await conn.run_sync(SQLModel.metadata.create_all)
```

这里连接对象代表异步连接，而要运行的 `create_all` 是同步函数。SQLModel 库写出的这个函数是阻塞的，在异步上下文中直接运行会阻塞；如果要在异步引擎上下文中运行同步函数，就要使用 `run_sync` 并传入未调用的函数。这个操作与之前同步版本做的事情完全相同：让引擎知道所有映射到数据库表的 SQLModel，并告诉数据库连接创建所有对应表。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_6.png)

![](img/86754ea2b9a04286ccbb50af3bc3a46e_7.png)

建表函数改好后，需要在 `main.py` 启动应用时调用 `create_db_and_tables`。函数内部把未调用的 `SQLModel.metadata.create_all` 传给 `run_sync`。这与之前的操作相同，只是现在在异步上下文中完成，因此可以删除旧的那行建表代码，以后基本不用再担心这块代码。

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield
```

建表逻辑完成后，同样要把 `get_session` 函数改成异步。因为现在使用的是异步数据库引擎，它会提供异步数据库会话，这个会话上的 `get` 或 `commit` 等方法可以用 `await` 等待。下面列出会话依赖改造中的几个关键点。

- 给 `get_session` 加上 `async` 关键字，让它成为异步函数。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_9.png)

- 使用 `async with` 创建异步上下文管理器。

- 从 `sqlmodel.ext.asyncio.session` 导入 `AsyncSession`。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_11.png)

- 实例化 `AsyncSession` 时传入异步引擎。

- 仍然用 `yield` 把会话交给路由处理器，并在结束后执行清理。

- 把 `SessionDep` 的类型从 `Session` 改成 `AsyncSession`。

导入和会话函数可以写成下面这样。

```python
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_session():
    async with AsyncSession(engine) as session:
        yield session
```

![](img/86754ea2b9a04286ccbb50af3bc3a46e_13.png)

`AsyncSession` 这个类表示一次与数据库的临时通信。项目里只有一个引擎，但每次访问端点时都会得到一个全新的会话，可以在这个会话上调用各种与数据库交互的方法。实例化异步会话时，和下面的同步写法一样传入引擎，只不过这里传入的是异步引擎，并把会话赋给 `session` 这个名字。注意差异：`with` 前多了 `async`，类名是 `AsyncSession`，变量名仍然是 `session`，原则完全相同，只是换成了异步版本。原来的同步会话行可以删除，仍然用 `yield` 返回会话。

当路由处理器执行完成并把会话交回后，`async with` 会执行清理，确保数据库连接正确终止，相关资源都被清理干净。现在有了异步引擎，这个函数就能提供支持 `await` 方法的异步会话。最后要更新会话依赖的类型注解，它不再返回 `Session`，而是返回 `AsyncSession`。在 `Annotated` 后面方括号里的第一个值改为 `AsyncSession`，同时删除不再需要的 `Session` 导入。

```python
SessionDep = Annotated[AsyncSession, Depends(get_session)]
```

到这里，`database.py` 中的一次性重构和更新就完成了。现在数据库连接、引擎和会话都是异步的，数据库层相关设置已经全部更新。之后路由处理器收到的会话会是 `AsyncSession`，它是会话对象的异步替代版本；`get` 或 `commit` 这类需要与数据库通信、会产生 I/O 等待的方法，在异步会话对象上都是非阻塞的异步方法。

当路由处理器中的代码暂停并等待数据库响应时，Python 的异步事件循环和 FastAPI 可以在这些毫秒级等待时间里，把其他任务排进同一个线程去处理。等所有路由处理器都更新完成后，数据库 I/O 操作就不会再阻塞，全部变成异步操作，因此在等待数据库时，另一个任务可以继续完成。

![](img/86754ea2b9a04286ccbb50af3bc3a46e_15.png)

![](img/86754ea2b9a04286ccbb50af3bc3a46e_17.png)

本节课中我们一起学习了如何将 FastAPI 的数据库层升级为异步，包括使用 `aiosqlite` 配置异步 SQLite 连接、用 `create_async_engine` 替换同步引擎、用 `run_sync` 在异步上下文中执行同步建表函数、用 `AsyncSession` 替换同步会话，以及更新依赖注入中的类型注解。完成这些改造后，路由层拿到的就是异步会话，数据库 I/O 不再阻塞事件循环。

