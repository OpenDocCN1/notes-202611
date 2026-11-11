

# 📊 Polars与Python数据分析：112：join_asof方法之三：by参数

## 🧭 Polars与Python数据分析：112.1：课程概述

在本节课中我们将要学习`join_asof`方法的一个限制，以及解决这个限制的办法。这个限制不是语法错误，而是它默认只关心时间上的接近程度，可能忽略业务字段是否真正匹配，因此会给出看似正确、实际不准确的结果。为了把问题讲清楚，我们会先导入两个互补的数据集，一个是交易流水，一个是汇率数据，然后演示只用常规参数会出现什么问题。接着我们会引入`by`参数，让Polars先按货币做精确匹配，再按时间做邻近匹配，最后计算每笔交易换算成美元后的总支付金额。本节先建立整体图景，接下来我们看看第一个数据集如何导入。

![](img/dd264ee518abc380b444c97cb01d0650_1.png)

## 📥 Polars与Python数据分析：112.2：导入交易数据

![](img/dd264ee518abc380b444c97cb01d0650_3.png)

上一节我们说明了本课程要解决的问题，本节先导入第一个数据集。第一个数据集位于`exchange_rates`目录中，文件名是`transactions.csv`，它是一组虚构的交易记录。每一笔交易都发生在某个具体时间点，并且有一个消费金额，这个金额由`currency`列指定的货币表示。例如某一行金额是270，另一行金额是267日元，这些金额都要结合对应货币来理解。读入数据时，我们立即传入`try_parse_dates=True`，确保`timestamp`列被读取为日期时间类型，而不是普通字符串。随后把结果赋值给`transactions`变量，并且在导入阶段就按`timestamp`列排序，让交易记录保持一致的升序顺序。最后预览交易数据框的前三行，确认数据长什么样。

```python
import polars as pl

transactions = (
    pl.read_csv(
        "exchange_rates/transactions.csv",
        try_parse_dates=True
    )
    .sort("timestamp")
)

transactions.head(3)
```

完成交易数据导入后，下一步自然要导入汇率数据。第二个数据集同样位于`exchange_rates`目录中，文件名是`rates.csv`。下面我们看看它的结构，以及它如何与交易数据配合。

## 💱 Polars与Python数据分析：112.3：导入汇率数据

![](img/dd264ee518abc380b444c97cb01d0650_5.png)

上一节我们导入了交易流水，本节来看汇率数据集。第二个数据集同样位于`exchange_rates`目录，文件名为`rates.csv`，它是一组汇率记录。在这些给定时间戳上，每一行表示一单位某种货币值多少美元，也就是说，它给出的是该货币兑美元的换算率。例如在某个时刻，1单位该货币等于1.09美元。和交易数据一样，我们也要传入`try_parse_dates=True`，并按`timestamp`列排序。然后把数据框赋值给`exchange_rates`变量，并预览内容。此时两个数据集都准备好了，但目标不是简单拼接，而是为每笔交易找到同一货币下时间最接近的汇率，从而得到最准确的美元换算金额。

```python
exchange_rates = (
    pl.read_csv(
        "exchange_rates/rates.csv",
        try_parse_dates=True
    )
    .sort("timestamp")
)

exchange_rates.head()
```

两个数据集都导入完成后，我们就能看到核心任务：把交易金额按最接近时间的汇率换算成美元。接下来先按最直接的方式调用`join_asof`，看看问题出在哪里。

## 🎯 Polars与Python数据分析：112.4：目标与默认参数的问题

上一节我们准备好了交易数据和汇率数据，本节说明目标以及默认参数下的问题。我们的目标是合并这两个数据集：对任意一笔交易，找到该交易货币兑美元的互补换算率，并在汇率表中找到时间最接近的那条记录，从而把该货币金额换算成等值美元金额。听起来很直接，但如果只使用`join_asof`的常规参数，就会出现一个明显问题。我们先在`transactions`上调用`join_asof`，因为要做的是基于两个表`timestamp`列的邻近连接。右表设为`exchange_rates`，`on`参数指定为`timestamp`，这个列名在左右两个表中完全相同。对于交易表中的任意时间戳，我们希望沿着时间向前回溯，直到在汇率表中找到最近的时间点，因此`strategy`参数设为`backwards`。为了让重复列保留下来便于观察，我们添加`coalesce=False`，这样右表中与左表同名的列也会带过来。为了说明这些列来自右表，还可以使用`suffix`参数，例如给重复列加上`_from_exchange_rates`后缀。执行后，第二行就会暴露问题：这笔交易发生在当天第30分钟，向前回溯找到的汇率表最近时间是午夜，但货币列被完全忽略了。交易表里这笔交易是欧元，汇率表里匹配到的却是日元汇率；时间匹配正确，货币值却没有保证相等。我们不想把欧元金额按日元汇率换算，那样会严重不准确，我们希望欧元交易匹配欧元汇率，同时仍然遵循上一课介绍的`join_asof`时间邻近逻辑。当前`join_asof`只关心时间上的邻近，也就是从交易时间向前回溯时遇到的最近时间，因此Polars基本忽略了`currency`列的取值，结果自然不准确。

```python
bad_joined = transactions.join_asof(
    exchange_rates,
    on="timestamp",
    strategy="backwards",
    coalesce=False,
    suffix="_from_exchange_rates"
)

bad_joined
```

![](img/dd264ee518abc380b444c97cb01d0650_7.png)

![](img/dd264ee518abc380b444c97cb01d0650_8.png)

> 关键问题：`join_asof`默认只按时间邻近回溯，不会自动保证货币等其他业务字段相等。

既然问题已经定位，解决办法分两步走：先重新导入数据并做好排序，再在`join_asof`中加入`by`参数。下面先看重新导入和排序的规则。

## 🧹 Polars与Python数据分析：112.5：重新导入并排序数据

上一节我们看到了货币被忽略导致的结果偏差，本节开始修复。第一步是重新导入两个数据集，并且在导入阶段应用更严格的排序逻辑。原因是我们需要先按货币列做一次严格的等值连接，让搜索范围缩小到同一种货币；例如欧元交易只在欧元汇率中搜索，日元交易只在日元汇率中搜索。完成这个子集筛选后，再在这个子集内做真正的时间邻近连接。为了让后续的`join_asof`正常工作，必须先按将要用于精确等值连接的列排序，然后再按时间戳列排序。对本例来说，两个表都先用`currency`排序，再在每种货币内部按`timestamp`排序。这个排序顺序不是可选项，而是下一步`join_asof`能够正确工作的必要条件。

![](img/dd264ee518abc380b444c97cb01d0650_10.png)

以下是重新导入和排序时需要遵循的规则：

![](img/dd264ee518abc380b444c97cb01d0650_11.png)

![](img/dd264ee518abc380b444c97cb01d0650_13.png)

- 先按用于严格等值连接的`currency`列排序，让同一种货币的记录聚在一起。

- 再在每种货币内部按`timestamp`列排序，为后面的时间邻近回溯做好准备。

- 交易表和汇率表都要采用同样的排序顺序。

```python
transactions = (
    pl.read_csv(
        "exchange_rates/transactions.csv",
        try_parse_dates=True
    )
    .sort(["currency", "timestamp"])
)

exchange_rates = (
    pl.read_csv(
        "exchange_rates/rates.csv",
        try_parse_dates=True
    )
    .sort(["currency", "timestamp"])
)
```

![](img/dd264ee518abc380b444c97cb01d0650_15.png)

![](img/dd264ee518abc380b444c97cb01d0650_17.png)

数据已经按“先货币、后时间”的规则排好，接下来就可以在`join_asof`中加入`by`参数。这个参数负责先做精确等值匹配，然后再执行时间邻近连接。

## 🔗 Polars与Python数据分析：112.6：使用by参数完成双重连接

上一节我们重新导入并排序了两个数据集，本节把`by`参数加进`join_asof`。把前面的连接代码复制过来后，只加一个参数就能让它按预期工作，这个参数就是`by`。在`by`中传入用于严格等值连接的列，也就是交易表和汇率表共有的`currency`列。这样Polars会先以`currency`为基础做精确匹配，再在匹配完成后的范围内，按共享的`timestamp`列向前回溯，寻找交易时间最接近的汇率记录。这个例子中两个表的列名相同，所以直接写`by="currency"`即可；如果列名不同，可以使用配套的`by_left`和`by_right`，分别指定左表和右表的列名，逻辑完全一样。无论列名是否相同，Polars都会先用`by`参数族完成等值连接，再用`on`参数完成基于时间的邻近连接。

```python
joined = transactions.join_asof(
    exchange_rates,
    on="timestamp",
    by="currency",
    strategy="backwards",
    coalesce=False,
    suffix="_from_exchange_rates"
)

joined
```

![](img/dd264ee518abc380b444c97cb01d0650_19.png)

![](img/dd264ee518abc380b444c97cb01d0650_20.png)

![](img/dd264ee518abc380b444c97cb01d0650_21.png)

![](img/dd264ee518abc380b444c97cb01d0650_22.png)

![](img/dd264ee518abc380b444c97cb01d0650_23.png)

执行这段代码后，结果应该同时满足两个条件：货币相同，并且时间最接近。接下来我们验证一下欧元交易是否真的匹配到了欧元汇率，而不是只凭感觉相信结果。

![](img/dd264ee518abc380b444c97cb01d0650_25.png)

## ✅ Polars与Python数据分析：112.7：验证连接结果

上一节我们加入了`by`参数，本节验证它是否按预期工作。为了证明结果正确，可以查看结果中大量欧元记录，也可以回到原始`exchange_rates`数据框，筛选`currency`等于欧元代码`EUR`的行，比较几行就能确认Polars有没有正确匹配。第一笔交易发生在2026年1月2日0点13分，货币是欧元。查看所有欧元汇率后，从当天第13分钟向前回溯，最近的时间点是午夜，对应汇率是1.09。再看连接结果中这一行，确实拿到了正确的1.09汇率。这说明Polars现在会先确认货币列中存在匹配值，再执行时间邻近连接。可以把这个过程理解成两个顺序连接：先做一次常规等值连接，再做一次基于时间的邻近连接。验证步骤如下。

以下是验证匹配结果的步骤：

- 从原始汇率表中筛选出欧元汇率，确认欧元汇率的时间点和数值。

- 在连接结果中定位第一笔欧元交易，检查它拿到的汇率是否为最近时间点的汇率。

![](img/dd264ee518abc380b444c97cb01d0650_27.png)

- 对比交易时间、汇率时间和汇率值，确认货币与时间两个条件同时满足。

![](img/dd264ee518abc380b444c97cb01d0650_29.png)

```python
exchange_rates.filter(
    pl.col("currency") == "EUR"
).head()
```

![](img/dd264ee518abc380b444c97cb01d0650_30.png)

![](img/dd264ee518abc380b444c97cb01d0650_31.png)

验证通过后，最后一步是把换算后的总支付金额计算出来，让整个示例形成完整闭环。

## 🧮 Polars与Python数据分析：112.8：计算总支付金额

上一节我们验证了`by`参数的效果，本节完成示例的最后一步：计算实际总支付金额。使用`with_columns`方法添加一个新列，表达式针对`amount`列，这个列表示某种货币下的金额，例如欧元金额。然后把`amount`乘以美元汇率列中的值，这个汇率现在可以确认是同一货币下时间最近的换算率。因为在表达式中使用了乘法运算符，需要用括号把整个表达式包起来，再用`alias`给新列命名，例如命名为`total_paid_in_USD`。关闭括号时可能多一个或少一个括号，调整到语法正确即可。完成后就能看到以美元表示的总支付金额，它由金额乘以对应汇率得到。这里的关键点是：乘上去的汇率必须是精确货币下时间最接近的汇率，这样换算才最准确。

核心计算公式可以写成下面这样：

![](img/dd264ee518abc380b444c97cb01d0650_33.png)

![](img/dd264ee518abc380b444c97cb01d0650_34.png)

![](img/dd264ee518abc380b444c97cb01d0650_35.png)

![](img/dd264ee518abc380b444c97cb01d0650_36.png)

![](img/dd264ee518abc380b444c97cb01d0650_37.png)

```text
total_paid_in_USD = amount × usd_rate
```

对应代码如下：

![](img/dd264ee518abc380b444c97cb01d0650_39.png)

![](img/dd264ee518abc380b444c97cb01d0650_40.png)

![](img/dd264ee518abc380b444c97cb01d0650_41.png)

```python
result = joined.with_columns(
    (pl.col("amount") * pl.col("usd_rate")).alias("total_paid_in_USD")
)

result
```

至此，交易数据、汇率数据、双重连接和金额换算都完成了。最后我们总结`join_asof`的这个限制，以及`by`参数的使用要点。

![](img/dd264ee518abc380b444c97cb01d0650_43.png)

![](img/dd264ee518abc380b444c97cb01d0650_44.png)

## 📌 Polars与Python数据分析：112.9：限制收尾与课程总结

上一节我们算出了美元总支付金额，本节收尾并总结。`join_asof`的这个特性可以看作一个需要留意的限制或特殊行为：如果需要在更小的子集内搜索，或者必须先做精确等值匹配，就要使用`by`参数完成等值连接，然后再用常规的`on`参数完成时间邻近连接。换句话说，`join_asof`并不是只能按时间连接，它可以在`by`参数的控制下先缩小匹配范围，再在范围内找最近时间。这个“先精确、再邻近”的顺序，是理解本课示例的关键。

> `join_asof` 的核心用法可以概括为：先按 `by` 做等值匹配，再按 `on` 做时间邻近回溯。

![](img/dd264ee518abc380b444c97cb01d0650_46.png)

![](img/dd264ee518abc380b444c97cb01d0650_47.png)

本节课中我们一起学习了`join_asof`方法在忽略业务字段时可能出现的不准确结果，也学习了如何通过重新排序数据并使用`by`参数，让Polars先按货币精确匹配，再按时间邻近回溯，最终正确计算每笔交易换算成美元后的总支付金额。掌握这个顺序后，面对“既要字段相等、又要时间最近”的连接需求，就可以更稳妥地使用`join_asof`。

