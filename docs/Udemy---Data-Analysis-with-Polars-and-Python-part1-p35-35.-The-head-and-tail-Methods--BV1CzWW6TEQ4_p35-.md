
# 📊 使用Polars和Python进行数据分析：35：Head和Tail方法

![](img/51d175cf04b09695275c0bed417ee06c_1.png)

在本节课中，我们将学习Polars中用于从序列开头或结尾提取指定行数的`head`和`tail`方法。我们还会介绍与`head`等价的`limit`别名，以及用于获取单个条目的`first`和`last`方法。这些方法在数据清洗和快速查看数据时非常实用。

![](img/51d175cf04b09695275c0bed417ee06c_3.png)

![](img/51d175cf04b09695275c0bed417ee06c_4.png)

![](img/51d175cf04b09695275c0bed417ee06c_5.png)

![](img/51d175cf04b09695275c0bed417ee06c_6.png)

首先，我们回顾上一节课编写的代码，因为接下来的所有示例都建立在这段代码之上。使用`read_csv`函数可以将CSV文本文件读取为一个Polars DataFrame，随后用`to_series`方法将单列DataFrame转换为Polars Series。于是，我们得到了一个名为`ice_creams`的序列。

![](img/51d175cf04b09695275c0bed417ee06c_7.png)

![](img/51d175cf04b09695275c0bed417ee06c_8.png)

```python
import polars as pl

df = pl.read_csv("ice_creams.csv")
ice_creams = df.to_series()
```

当我们在环境中直接输出`ice_creams`时，默认情况下Polars会显示前5行，接着是一个由省略号组成的间隔行，最后显示后5行。这种显示方式让我们既能快速了解数据开头，也能看到结尾，同时避免刷屏。这个默认行为只是显示层面的，并不会改变序列本身，而我们接下来要学习的`head`和`tail`方法则会真正返回一个新序列。

![](img/51d175cf04b09695275c0bed417ee06c_10.png)

![](img/51d175cf04b09695275c0bed417ee06c_11.png)

![](img/51d175cf04b09695275c0bed417ee06c_12.png)

了解了默认显示后，我们来看看如何从序列的头部提取指定行数。对`ice_creams`调用`head`方法，如果不传任何参数，它会返回原序列的前10行，这是一个形状为10行的新序列。这10行的内容就是原序列的第1到第10个元素。我们可以将`head(10)`的前5个值与默认显示的前5个值对比，两者完全一致，这验证了取值的正确性。

![](img/51d175cf04b09695275c0bed417ee06c_14.png)

通过编辑器中的Shift+Tab快捷键，我们可以查看`head`方法的文档。文档显示，该方法只接受一个参数`n`，用于指定从序列顶部提取多少行。`n`的默认值是10，所以直接调用`head()`就能得到前10行。当然，我们完全可以传入不同的数值来改变结果。以下是`head`方法在不同参数下的调用示例：

- `ice_creams.head()`：返回前10行，因为`n`默认为10。
- `ice_creams.head(5)`：返回前5行。
- `ice_creams.head(3)`：返回前3行。
- `ice_creams.head(n=7)`：显式指定`n=7`，返回前7行。

![](img/51d175cf04b09695275c0bed417ee06c_16.png)

![](img/51d175cf04b09695275c0bed417ee06c_17.png)

![](img/51d175cf04b09695275c0bed417ee06c_18.png)

除了`head`，Polars的Series还提供了`limit`方法。`limit`实际上是`head`的别名，所谓别名，就是同一功能的另一个名字，两者完全等价。Polars团队之所以加入`limit`这个名字，是为了匹配SQL中经常使用的术语。在SQL中，我们通常用`LIMIT`关键字来限制查询返回的总行数；在Polars中，`limit`方法的核心思想也完全一样。下面这个例子中，我们调用`limit(7)`，它同样从序列开头提取前7行，得到的结果与`head(n=7)`完全一致。

![](img/51d175cf04b09695275c0bed417ee06c_19.png)

![](img/51d175cf04b09695275c0bed417ee06c_20.png)

![](img/51d175cf04b09695275c0bed417ee06c_21.png)

```python
ice_creams.limit(7)  # 等价于 ice_creams.head(7)
```

接下来，我们来看看与`head`相反的`tail`方法。`tail`从原序列的末尾提取行，正好与`head`相对。它的参数`n`默认值同样为10，所以`ice_creams.tail()`会返回原序列的最后10行。如果传入3，就可以提取最后3条记录；如果使用关键字参数指定`n=4`，则会提取最后4行。下面是这几个调用的示例：

![](img/51d175cf04b09695275c0bed417ee06c_23.png)

![](img/51d175cf04b09695275c0bed417ee06c_24.png)

```python
ice_creams.tail()     # 返回最后10行
ice_creams.tail(3)    # 返回最后3行
ice_creams.tail(n=4)  # 返回最后4行
```

`head`和`tail`还有一个有趣的性质：它们都支持负数参数。这是一个比较特别的使用方式，需要稍加解释。传入负数时，意思并不是提取负数行，而是排除末端若干行。例如`head(-3)`，Polars会从序列开头开始提取，一直提取到倒数第3行之前为止，相当于排除末尾的3行。再比如`tail(-3)`，Polars会从序列末尾开始提取，一直提取到正数第3行之后为止，相当于排除开头的3行。由于原序列共有1000行，`head(-3)`和`tail(-3)`都会得到997行的新序列。

![](img/51d175cf04b09695275c0bed417ee06c_26.png)

![](img/51d175cf04b09695275c0bed417ee06c_27.png)

![](img/51d175cf04b09695275c0bed417ee06c_28.png)

![](img/51d175cf04b09695275c0bed417ee06c_29.png)

用公式可以更清晰地表达这两个行为：

```
head(-n) = series[0 : len(series)-n]
tail(-n) = series[n : len(series)]
```

![](img/51d175cf04b09695275c0bed417ee06c_31.png)

![](img/51d175cf04b09695275c0bed417ee06c_32.png)

![](img/51d175cf04b09695275c0bed417ee06c_33.png)

![](img/51d175cf04b09695275c0bed417ee06c_34.png)

上面两个公式中，`n`表示传入的负数绝对值，`len(series)`表示原序列的总行数。当`n=3`时，`head(-3)`的结果是原序列的第1行到第997行，而`tail(-3)`的结果是原序列的第4行到第1000行。你可能会注意到，`tail(-3)`的结果最后一项是`blueberry flake delight`，这正是原序列的最后一个条目，因为我们取了从第4行到末尾的所有内容，同时忽略了前3行。总而言之，`head`和`tail`对负数的支持让我们可以很方便地剔除头部或尾部的若干行。

有时候，我们只需要取出序列中的第一个或最后一个值，而不想关心返回的序列到底包含多少行。针对这种需求，Polars提供了`first`和`last`方法，名字非常直观。这两个方法有一个重要区别需要牢记：`head`始终返回一个新的Series，即使你传入了参数`1`，它返回的仍然是一个只包含一个元素的Series；而`first`直接返回实际的行条目，也就是那个具体的值。由于`ice_creams`是一个字符串序列，因此`first`返回的就是第一个字符串条目。在我们的示例中，`ice_creams.first()`会得到`cherry trip drizzle`。与`first`互补的`last`方法，则返回序列中的最后一个条目，这里得到的是`cinnamon chumb magic`。它们不会创建新序列，只是把原始条目提取出来而已。

![](img/51d175cf04b09695275c0bed417ee06c_36.png)

![](img/51d175cf04b09695275c0bed417ee06c_37.png)

![](img/51d175cf04b09695275c0bed417ee06c_38.png)

![](img/51d175cf04b09695275c0bed417ee06c_39.png)

```python
ice_creams.first()  # 返回第一个条目：'cherry trip drizzle'
ice_creams.last()   # 返回最后一个条目：'cinnamon chumb magic'
```

![](img/51d175cf04b09695275c0bed417ee06c_41.png)

本节课中，我们一起学习了Polars中用于数据提取的几个重要方法。`head`和`tail`可以从序列的开头或结尾提取指定行数，`limit`是`head`的别名，适合熟悉SQL的朋友使用。`first`和`last`则用于快速获取单个条目。这些方法帮助我们方便地在Polars数据结构的开头或末尾提取数据，是日常数据分析中非常实用的小工具。
