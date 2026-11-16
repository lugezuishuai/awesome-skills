# 重构手法名录（61 个）

提炼自《重构（第 2 版）》第 6–12 章，按 7 大类组织。每个手法一句话说明“做什么 / 何时用”。
当你已经决定要改、想找对应手法时查此表；判断“哪里该改”请看 `code-smells.md`。

类别：
- A. 第一组重构（基础）
- B. 封装
- C. 搬移特性
- D. 重新组织数据
- E. 简化条件逻辑
- F. 重构 API
- G. 处理继承关系

> 通用心法：每个手法都用一连串**小而保持行为不变**的步骤完成，每步之后代码仍可运行、可测试。

---

## A. 第一组重构（基础）

- **提炼函数（Extract Function）** — 把一段代码抽成独立函数，按“用途”而非实现命名。最常用。
- **内联函数（Inline Function）** — 把函数调用替换为其函数体，去掉不增值的间接。
- **提炼变量（Extract Variable）** — 给复杂表达式的一部分引入解释性的命名变量。
- **内联变量（Inline Variable）** — 把只是复述表达式的变量替换回表达式本身。
- **改变函数声明（Change Function Declaration）** — 修改函数名或参数列表（含函数改名、增删参数）。
- **封装变量（Encapsulate Variable）** — 用访问函数包裹数据，收拢并监控对它的读写。
- **变量改名（Rename Variable）** — 给变量换一个能表达意图的名字。
- **引入参数对象（Introduce Parameter Object）** — 把总是同时出现的一组参数合并为一个对象。
- **函数组合成类（Combine Functions into Class）** — 把操作同一组数据的函数与数据组织成一个类。
- **函数组合成变换（Combine Functions into Transform）** — 把对源数据的多处派生计算集中到一个变换函数。
- **拆分阶段（Split Phase）** — 把交织的代码拆成顺序两阶段，中间用清晰的数据结构衔接。

## B. 封装

- **封装记录（Encapsulate Record）** — 用类取代可变的记录 / 裸数据结构。
- **封装集合（Encapsulate Collection）** — 不直接暴露集合：提供增删方法，对外返回副本或只读视图。
- **以对象取代基本类型（Replace Primitive with Object）** — 把简单数据值升级为可承载行为的领域对象。
- **以查询取代临时变量（Replace Temp with Query）** — 把临时变量改为可复用的查询函数。
- **提炼类（Extract Class）** — 把一个类中彼此相关的字段与函数拆到新类。
- **内联类（Inline Class）** — 把职责已不足的类并回使用它的类。
- **隐藏委托关系（Hide Delegate）** — 在服务对象上加方法隐藏其背后的委托对象，斩断消息链。
- **移除中间人（Remove Middle Man）** — 让客户端直接调用真正负责的对象，去掉纯转发方法。
- **替换算法（Substitute Algorithm）** — 用更清晰、更简单的算法替换函数体。

## C. 搬移特性

- **搬移函数（Move Function）** — 把函数移到它更该归属的模块 / 类（常用于治“依恋情结”）。
- **搬移字段（Move Field）** — 把字段移到更合适的数据结构。
- **搬移语句到函数（Move Statements into Function）** — 把每个调用处都重复的语句并入被调函数。
- **搬移语句到调用者（Move Statements to Callers）** — 把不该被所有调用者共有的语句移回各调用处。
- **以函数调用取代内联代码（Replace Inline Code with Function Call）** — 用已有函数替换与之等价的内联代码。
- **移动语句（Slide Statements）** — 把相关的语句挪到一起，为后续提炼做准备。
- **拆分循环（Split Loop）** — 让一个循环只做一件事；做多件事时拆成多个循环。
- **以管道取代循环（Replace Loop with Pipeline）** — 用 map / filter / reduce 等集合管道取代命令式循环。
- **移除死代码（Remove Dead Code）** — 删掉不再被使用的代码。

## D. 重新组织数据

- **拆分变量（Split Variable）** — 一个变量被复用于多种用途时，按用途拆成多个变量。
- **字段改名（Rename Field）** — 给字段换一个能表达意图的名字。
- **以查询取代派生变量（Replace Derived Variable with Query）** — 去掉可由计算得出的可变变量，改为按需计算。
- **将引用对象改为值对象（Change Reference to Value）** — 把内部对象当作不可变的值整体替换。
- **将值对象改为引用对象（Change Value to Reference）** — 让多处共享同一个对象实例，统一更新。

## E. 简化条件逻辑

- **分解条件表达式（Decompose Conditional）** — 把复杂的条件、各分支分别提炼成有名字的函数。
- **合并条件表达式（Consolidate Conditional Expression）** — 把结果相同的多个条件检查合并为一个。
- **以卫语句取代嵌套条件表达式（Replace Nested Conditional with Guard Clauses）** — 对特殊情况提前返回，消除深层嵌套。
- **以多态取代条件表达式（Replace Conditional with Polymorphism）** — 用多态分派取代重复的类型 / 条件分支。
- **引入特例（Introduce Special Case）** — 为反复处理的特例提供专门对象（特例 / 空对象模式）。
- **引入断言（Introduce Assertion）** — 用断言显式声明代码所依赖的前提条件。

## F. 重构 API

- **将查询函数和修改函数分离（Separate Query from Modifier）** — 让返回值的查询无副作用，与修改分开。
- **函数参数化（Parameterize Function）** — 把几个仅常量不同的相似函数合并为一个带参函数。
- **移除标记参数（Remove Flag Argument）** — 把用标记控制行为的参数拆成若干意图清晰的独立函数。
- **保持对象完整（Preserve Whole Object）** — 直接传入整个对象，而非先从中拆出几个值再传。
- **以查询取代参数（Replace Parameter with Query）** — 去掉可在函数内部查到的多余参数。
- **以参数取代查询（Replace Query with Parameter）** — 把对外部状态的内部查询改为由参数传入，降低依赖。
- **移除设值函数（Remove Setting Method）** — 去掉不应在构造后被修改的字段的设值函数。
- **以工厂函数取代构造函数（Replace Constructor with Factory Function）** — 用工厂函数取代构造函数，获得更灵活的创建逻辑。
- **以命令取代函数（Replace Function with Command）** — 把函数封装成命令对象，便于参数化、撤销、分步执行。
- **以函数取代命令（Replace Command with Function）** — 命令对象过重时还原为简单函数。

## G. 处理继承关系

- **函数上移（Pull Up Method）** — 把各子类中相同的函数提到超类。
- **字段上移（Pull Up Field）** — 把各子类中相同的字段提到超类。
- **构造函数本体上移（Pull Up Constructor Body）** — 把子类构造函数中重复的逻辑提到超类构造函数。
- **函数下移（Push Down Method）** — 把只与部分子类相关的函数下移到那些子类。
- **字段下移（Push Down Field）** — 把只与部分子类相关的字段下移。
- **以子类取代类型码（Replace Type Code with Subclasses）** — 用子类取代控制行为的类型码，配合多态。
- **移除子类（Remove Subclass）** — 价值不足的子类用超类中的字段取代。
- **提炼超类（Extract Superclass）** — 为有共性的两个类提炼出共同超类。
- **折叠继承体系（Collapse Hierarchy）** — 超类与子类差别不大时合并为一个。
- **以委托取代子类（Replace Subclass with Delegate）** — 用委托（组合）取代继承，关系更灵活。
- **以委托取代超类（Replace Superclass with Delegate）** — 用委托取代继承，避免“被拒绝的遗赠”。
