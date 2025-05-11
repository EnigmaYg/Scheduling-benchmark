# from matplotlib import pyplot as plt
# import numpy as np
#
# #参数设置
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False
# plt.rcParams['figure.dpi'] = 300
# plt.rcParams['figure.figsize'] = (5,3)
#
# #国家和奖牌数据导入
# countries = ['简单', '中等', '复杂']
# correct_list = [4236, 4794, 5488]
# wrong_list = [3406, 3719, 4720]
#
# #将横坐标国家转换为数值
# x = np.arange(len(countries))
# width = 0.2
#
# #计算每一块的起始坐标
# gold_x = x
# silver_x = x + width
#
# #绘图
# plt.bar(gold_x,correct_list,width=width,color="green",label="正确")
# plt.bar(silver_x,wrong_list,width=width,color="red",label="错误")
#
# #将横坐标数值转换为国家
# plt.xticks(x + width / 2, labels=countries)
#
# #显示柱状图的高度文本
# for i in range(len(countries)):
#     plt.text(gold_x[i],correct_list[i], correct_list[i],va="bottom",ha="center",fontsize=8)
#     plt.text(silver_x[i],wrong_list[i], wrong_list[i],va="bottom",ha="center",fontsize=8)
#
# #显示图例
# plt.legend(loc="best")
# plt.show()

import matplotlib.pyplot as plt

# 数据
labels = ['家居和花园', '个人护理和时尚', '食品和娱乐', '计算机和电子产品', '爱好和工艺品', '宠物和动物']  # 类别标签
sizes = [26.3, 2.3, 51.1, 0.4, 17.3, 2.6]       # 每个类别的占比
colors = ['gold', 'yellowgreen', 'lightcoral', 'lightskyblue', 'orange', 'purple']
explode = (0.1, 0, 0.1, 0, 0.1, 0)       # 突出显示第一个部分
plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为黑体，支持中文
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
plt.rcParams['figure.dpi'] = 300
# 绘制饼状图
plt.pie(sizes, explode=explode, labels=labels, colors=colors,
        autopct='%1.1f%%', shadow=True, startangle=140)

# 添加标题
plt.title('')

# 显示图形
plt.show()