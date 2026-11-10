
# 🧰 FastAPI Masterclass：Part 2 p08 109：提取错误

在本节课中，我们将暂时从数据库相关工作中抽身出来，做一个与错误处理有关的小型重构。这个重构的目标很直白：把散落在各个路由文件里的错误实例集中到一个单独的 Python 文件中，方便统一管理和复用。我们会先找到所有 `raise HTTPException(...)` 的用法，再把这些具体错误实例搬到一个专门的 `errors.py` 文件里，最后用常量替换原来的写法。下面我们开始。

## 🧭 FastAPI Masterclass：Part 2 p08 109：认识当前错误写法

上一段我们说明了本节课要做错误提取。本节中我们来看看代码库里现有的错误抛出方式。首先在代码库中搜索 `raise` 关键字后面跟着 `HTTPException` 类的所有用法。提醒一下，`HTTPException` 直接来自 FastAPI，它会在路由处理程序执行到该位置时抛出错误，并立即终止该路由，然后返回一个错误状态码。代码中能看到一些相似模式：房间不存在、用户不存在、房间/用户/预订不存在、独占维护模式异常、又一处用户不存在等。以下是这些重复模式的概括。

![](img/bc57e04b78c3a57f9d60c61086bce037_1.png)

- 房间不存在错误：`raise HTTPException(...)`
- 用户不存在错误：`raise HTTPException(...)`
- 房间、用户、预订不存在错误：多处类似写法
- 维护模式异常：`raise HTTPException(...)`
- 又一处用户不存在错误：`raise HTTPException(...)`

这些写法看起来很像，但消息细节可能有偏差，比如有的地方写 `room does not exist`，有的地方写 `room not found`。这种小偏差会让错误消息不一致。

![](img/bc57e04b78c3a57f9d60c61086bce037_3.png)

## 🧩 FastAPI Masterclass：Part 2 p08 109：为什么要集中错误

![](img/bc57e04b78c3a57f9d60c61086bce037_4.png)

上一节我们看到了错误写法散落的问题。本节中我们来看看集中错误的好处。我们希望只把这些类实例，也就是这些 `HTTPException(...)` 代码，移动到一个更小、更独立的错误文件中，把所有错误集中放在一起。这样做的直接好处是：可以在许多不同路由处理程序中复用完全一致、稳定的错误类，包括一致的消息文本。比如原来一个地方说 `room does not exist`，另一个地方说 `room not found`，立刻就有措辞偏差；把这些错误合并到一个文件后，就能确保复用完全相同的实例，减少措辞变化。核心思路可以用下面的伪代码表示。

![](img/bc57e04b78c3a57f9d60c61086bce037_6.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_7.png)

```python
# 重构前：每个路由里都手写错误
raise HTTPException(status_code=404, detail="Room not found")

# 重构后：统一从 errors.py 引入预实例化错误
from app.errors import ROOM_NOT_FOUND
raise ROOM_NOT_FOUND
```

## 🗂️ FastAPI Masterclass：Part 2 p08 109：创建 errors.py

![](img/bc57e04b78c3a57f9d60c61086bce037_9.png)

上一节我们说明了集中错误的理由。本节中我们开始在 `app` 目录中创建新文件。创建名为 `errors.py` 的新文件，然后逐个处理所有错误用法；如果是第一次遇到某个错误，就把它复制到这个新文件里。以下是创建常量的基本写法。

```python
from fastapi import HTTPException, status

ROOM_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Room not found",
)
```

![](img/bc57e04b78c3a57f9d60c61086bce037_11.png)

这里先把第一个错误复制过来，并赋值给一个常量，常量名写成大写，例如 `ROOM_NOT_FOUND`。为了让编辑器里的未定义警告消失，需要两个导入：从 `fastapi` 引入 `HTTPException`，以及引入 `status` 模块。接着已经知道还有两个错误与系统中的另外两个资源有关，因此复制两次并更新术语：`ROOM_NOT_FOUND`、`USER_NOT_FOUND`、`BOOKING_NOT_FOUND`。消息可以保持一致的格式，例如用户不存在就用统一的 `User not found`。最后还有维护模式错误，它在房间路由中出现，也复制到 `errors.py`，赋值给常量 `SERVICE_UNDER_MAINTENANCE`。以下是集中后的错误常量示例。

![](img/bc57e04b78c3a57f9d60c61086bce037_13.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_14.png)

```python
from fastapi import HTTPException, status

ROOM_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Room not found",
)

USER_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="User not found",
)

BOOKING_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Booking not found",
)

SERVICE_UNDER_MAINTENANCE = HTTPException(
    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    detail="Service under maintenance",
)
```

## 🔁 FastAPI Masterclass：Part 2 p08 109：替换各路由中的错误

上一节我们创建了集中错误常量。本节中我们要把各个路由中 `HTTPException` 类的实例替换成这些硬编码常量。先从房间相关代码开始。这里需要 `ROOM_NOT_FOUND` 错误，因此从 `app` 包的 `errors` 文件引入 `ROOM_NOT_FOUND`。它是一个预实例化的类实例，状态码和 `detail` 都已经填好，因此可以直接写 `raise ROOM_NOT_FOUND`。这样还可以移除不再需要的导入，例如 `HTTPException` 和 `status`，从而让文件更干净。以下是替换前后对照。

```python
# 替换前
from fastapi import HTTPException, status

raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Room not found",
)

# 替换后
from app.errors import ROOM_NOT_FOUND

raise ROOM_NOT_FOUND
```

![](img/bc57e04b78c3a57f9d60c61086bce037_16.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_17.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_18.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_19.png)

接下来看用户相关文件。这里需要对应的用户不存在异常。同样从 `app.errors` 引入 `USER_NOT_FOUND` 这个 `HTTPException` 实例，然后写 `raise USER_NOT_FOUND`。`raise` 关键字后跟某个错误类实例的语法保持不变，这个实例可以来自 Python 内置错误类，也可以来自 FastAPI 提供的错误类。这里同样可以移除不再需要的 `HTTPException` 和 `status` 导入。以下是用户路由的替换思路。

```python
from app.errors import USER_NOT_FOUND

raise USER_NOT_FOUND
```

继续看预订相关文件。这里实际会用到房间不存在、用户不存在和预订不存在三个错误。需要从 `app.errors` 导入 `BOOKING_NOT_FOUND`、`ROOM_NOT_FOUND` 和 `USER_NOT_FOUND`，然后替换下面所有用法。具体来说，如果房间不存在，就抛出 `ROOM_NOT_FOUND`；如果用户不存在，就抛出 `USER_NOT_FOUND`；如果预订不存在，就抛出 `BOOKING_NOT_FOUND`。这样做还能清理代码，因为类本身封装了状态码和详情等信息，不必在多行里重复写。以下是预订路由中常见的替换方式。

![](img/bc57e04b78c3a57f9d60c61086bce037_21.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_22.png)

```python
from app.errors import BOOKING_NOT_FOUND, ROOM_NOT_FOUND, USER_NOT_FOUND

if not room:
    raise ROOM_NOT_FOUND

if not user:
    raise USER_NOT_FOUND

if not booking:
    raise BOOKING_NOT_FOUND
```

![](img/bc57e04b78c3a57f9d60c61086bce037_24.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_25.png)

完成替换后，检查文件顶部导入，不再需要 `HTTPException` 和 `status`，可以把它们删掉。以下是清理导入的示意。

```python
# 删除不再需要的导入
# from fastapi import HTTPException, status
```

![](img/bc57e04b78c3a57f9d60c61086bce037_27.png)

## 🛠️ FastAPI Masterclass：Part 2 p08 109：处理维护模式与用户路由

![](img/bc57e04b78c3a57f9d60c61086bce037_28.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_29.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_30.png)

上一节我们替换了房间、用户和预订中的主要错误。本节中我们继续处理维护模式和用户路由。房间路由这里只需要使用服务维护错误，没有其他错误。因此从 `app.errors` 引入 `SERVICE_UNDER_MAINTENANCE`，然后在检查维护模式的依赖函数中写 `raise SERVICE_UNDER_MAINTENANCE`。这样也可以移除 `HTTPException` 导入。以下是维护模式依赖中的写法。

```python
from app.errors import SERVICE_UNDER_MAINTENANCE

def check_maintenance_mode():
    if maintenance_mode_enabled:
        raise SERVICE_UNDER_MAINTENANCE
```

最后看用户路由，这里需要用户不存在错误。同样从 `app.errors` 引入 `USER_NOT_FOUND`，然后在对应位置写 `raise USER_NOT_FOUND`。这样每个文件都变得更短，也可以移除 `HTTPException` 的导入。以下是用户路由的简化结果。

![](img/bc57e04b78c3a57f9d60c61086bce037_32.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_33.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_34.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_35.png)

```python
from app.errors import USER_NOT_FOUND

raise USER_NOT_FOUND
```

![](img/bc57e04b78c3a57f9d60c61086bce037_36.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_37.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_38.png)

## ✅ FastAPI Masterclass：Part 2 p08 109：验证重构结果

![](img/bc57e04b78c3a57f9d60c61086bce037_40.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_42.png)

上一节我们完成了各文件替换。本节中我们来验证重构结果。现在再搜索 `raise HTTPException`，代码库里已经不再出现这种写法，因为 `raise` 后面现在跟着的是具体的、预先实例化的类实例。可以看到列出的都是我们已经替换过的用法。如果有需要，也可以把 `ValueError` 提取成自己的常量；目前先保留原样。至此重构完成，我们已把大量共享错误集中到专用的 Python 文件中。可以用下面的检查思路确认结果。

```python
# 搜索目标
raise HTTPException

# 期望结果
# 代码库中不再出现该模式
```

## 📚 FastAPI Masterclass：Part 2 p08 109：总结

![](img/bc57e04b78c3a57f9d60c61086bce037_44.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_45.png)

![](img/bc57e04b78c3a57f9d60c61086bce037_46.png)

本节课中我们一起学习了如何提取 FastAPI 应用中的错误。我们先找到所有 `raise HTTPException(...)` 的重复写法，理解了这些错误实例会在路由处理程序中立即终止执行并返回错误状态码。接着创建了 `app/errors.py`，把房间不存在、用户不存在、预订不存在和维护模式等错误集中为预实例化常量。随后在房间、用户、预订等路由中引入这些常量并替换原有写法，同时清理不再需要的导入。最后通过搜索确认 `raise HTTPException` 不再出现。这样代码更集中、错误消息更一致，也更便于后续复用和维护。

