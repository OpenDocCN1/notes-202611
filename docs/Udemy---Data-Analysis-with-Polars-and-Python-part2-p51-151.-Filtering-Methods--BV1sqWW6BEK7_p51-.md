
## 使用Polars和Python进行数据分析：第2部分·第151节：过滤方法 🔍

本节课我们一起来学习Polars中字符串过滤的几个常用方法。具体来说，我们会接触str命名空间下的contains、contains_any、starts_with和ends_with，并解决一个非常常见的问题——大小写敏感。通过这部分内容，你会知道如何从数据集中按字符串条件提取行，同时不会改动原始数据。

![](img/3a88ae1534d2c608a75ec8e238b6902b_1.png)

### 1. 过滤的基本逻辑

在开始动手写代码之前，我们先明确一下“过滤”到底是什么意思。所谓过滤，就是从原始的DataFrame中，按照一个或多个条件，提取出符合条件的行的子集。换句话说，最后得到的DataFrame里只包含那些让条件为真的行。

Polars中实现过滤的核心方法是filter。你只需要在原始DataFrame上调用filter，然后传入一个布尔表达式。Polars会对每一行计算这个表达式，如果结果是True就保留这一行，如果结果是False就丢弃这一行。这个逻辑可以这样描述：

```python
result = df.filter(condition)
```

其中condition是针对每一行的布尔表达式。无论你之后使用哪种字符串过滤方法，底层用的都是同一个filter机制，只不过condition的构造方式不同而已。这个基础逻辑非常简单，但却是很多复杂数据清洗操作的地基。

### 2. 使用str.contains进行子串匹配

在开始字符串过滤之前，我们先要认识一下str命名空间。在Polars里，字符串类型的列会有一个str属性，里面存放了很多专门处理字符串的方法。我们可以借助这些方法，构造出上一节所说的布尔表达式。

假设我们已经导入了一份名为nyc的DataFrame，这张表里有一列叫做title，存放的是员工的职位名称。现在，我想把所有职位名称中包含“water”的员工都挑出来。这里的“包含”指的是“water”出现在职位名称的任意位置：可以在开头，可以在结尾，也可以夹在中间。只要出现了就算。

要完成这个任务，我们可以用str.contains方法。先构造一个针对title列的表达式，再通过str属性调用contains，并传入我们要查找的子串“water”：

![](img/3a88ae1534d2c608a75ec8e238b6902b_3.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_4.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_5.png)

```python
nyc.filter(pl.col("title").str.contains("water"))
```

![](img/3a88ae1534d2c608a75ec8e238b6902b_7.png)

在这一行代码里，pl.col("title").str.contains("water")会产生一列布尔值。Polars看到True就保留对应行，看到False就剔除。最终得到的结果中，每一行的title字符串里一定都包含“water”。这个操作在数据清洗中很常见，比如通过关键词快速筛选相关记录。

不过这里有一个容易踩的坑：contains的匹配是大小写敏感的。它要求完全一致的字符序列，也就是大写W后跟着小写ater。当你的数据有600万行时，你根本没法保证所有文本的写法都统一。所以，我们一会儿会介绍怎么把搜索规范化。

![](img/3a88ae1534d2c608a75ec8e238b6902b_9.png)

### 3. 使用str.contains_any匹配多个子串

有时候，你想匹配的不止一个词。比如说，你想找出职位名称中包含“water”或“fire”的员工。当然你可以写两个条件然后用|连接，但更省事的方法是使用contains_any。这个方法接收一个列表，只要字符串中包含列表中任意一个元素，就返回True；如果一个都不包含，就返回False。

下面这段代码就展示了它的用法：

![](img/3a88ae1534d2c608a75ec8e238b6902b_11.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_12.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_13.png)

```python
nyc.filter(pl.col("title").str.contains_any(["water", "fire"]))
```

![](img/3a88ae1534d2c608a75ec8e238b6902b_15.png)

你可能会注意到，运行结果里似乎没看到含“water”的行，这其实只是巧合。因为返回结果先显示了匹配“fire”的行，而含“water”的行可能在后面。总之，contains_any可以让你在一个表达式里完成多个子串的匹配，非常方便。

### 4. 使用starts_with和ends_with进行位置匹配

contains和contains_any只关心“是否包含”，并不关心子串在字符串里的位置。但有时我们需要更精确的约束，比如只匹配以某个词开头的字符串，或者只匹配以某个词结尾的字符串。这时就要用到starts_with和ends_with。

![](img/3a88ae1534d2c608a75ec8e238b6902b_17.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_18.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_19.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_20.png)

先看starts_with。它检查每一行的字符串是否以指定的子串开头。例如，我们想找出所有职位名称以“fire”开头的员工：

```python
nyc.filter(pl.col("title").str.starts_with("fire"))
```

如果“fire”出现在词的中间或结尾，那就不满足条件。所有保留下来的行，其title字符串一定是在最开头就出现了“fire”。

![](img/3a88ae1534d2c608a75ec8e238b6902b_22.png)

与之对应的是ends_with。它检查字符串是否以指定的子串结尾。例如，我们想找出职位名称以“marshall”结尾的员工：

![](img/3a88ae1534d2c608a75ec8e238b6902b_23.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_24.png)

![](img/3a88ae1534d2c608a75ec8e238b6902b_25.png)

```python
nyc.filter(pl.col("title").str.ends_with("marshall"))
```

如果“marshall”出现在开头或中间，都不会匹配；只有它正好出现在字符串末尾时，条件才成立。这两个方法结合起来，可以处理很多位置相关的查询需求，比如查找特定前缀的职位代码或者特定后缀的文件名。

### 5. 大小写敏感问题与文本归一化

在刚才的例子中，我们直接搜索了小写的“fire”。但如果你真的在数据上执行，可能会惊讶地发现，结果是一个空DataFrame。这并不代表数据里没有以Fire开头的职位，而是因为数据中的实际写法是“Fire”——首字母大写，而我们搜索的是小写“fire”。

Polars的字符串匹配本质上是对字符的精确比较，所以大小写必须完全一致。这里有一个典型的解决方案：对文本做归一化，也就是把文本统一转换成全小写或全大写。转换之后，再去搜索对应的大小写形式。

![](img/3a88ae1534d2c608a75ec8e238b6902b_27.png)

先看转小写的方案。我们可以先调用str.to_lowercase()把title列的所有字符转换成小写，然后立刻接上starts_with("fire")：

```python
nyc.filter(pl.col("title").str.to_lowercase().str.starts_with("fire"))
```

注意，这里并不是真的把数据永久改成了小写。to_lowercase()只是为当前表达式临时生成一个全小写的版本，用来和“fire”比较。比较产生的布尔序列会被filter用来筛选原始行，原始DataFrame本身没有受到任何影响。你可以把它理解成“用一份临时的副本做匹配，然后从原件中取行”。

![](img/3a88ae1534d2c608a75ec8e238b6902b_29.png)

反过来，我们也可以把数据全转成大写，再用全大写的“FIRE”去匹配：

```python
nyc.filter(pl.col("title").str.to_uppercase().str.starts_with("FIRE"))
```

![](img/3a88ae1534d2c608a75ec8e238b6902b_31.png)

两种方式得到的结果一模一样，因为数据只是被“归一化”到了不同的方向。简单地说，你可以在全小写列里找小写词，也可以在全大写列里找大写词。这种临时转换的技巧，是处理脏文本时非常实用的手段。

### 6. 总结

本节课我们一起学习了Polars中与字符串过滤相关的几个核心方法。这里快速回顾一下：

![](img/3a88ae1534d2c608a75ec8e238b6902b_33.png)

- contains：判断字符串是否包含指定子串，位置不限。
- contains_any：判断字符串是否包含多个指定子串中的任意一个。
- starts_with：判断字符串是否以指定子串开头。
- ends_with：判断字符串是否以指定子串结尾。

![](img/3a88ae1534d2c608a75ec8e238b6902b_35.png)

我们还看到了大小写敏感带来的坑，以及如何用to_lowercase或to_uppercase进行文本归一化，从而绕过大小写问题。记住，这些转换都是临时的，不会改动原始数据。掌握了这些方法，你就能在处理文本数据时快速定位到需要的行，为后续的分析做好准备。
