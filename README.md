# python-elasticsearch
计算端口可用率

脚本原理：查询本月所有该端口down的时间戳，放在一个列表中，根据每个时间戳继续轮询该端口up的时间戳，取uptime>=downtime的部分，放在一个列表中排序，取第0个，计算差值，单位为s;可能某设备某端口一个月内也不会有一条日志出现在elk的情况，此时应判定端口可用率为 100% 或 0% 。

供测试使用



输出例示：

{'detail': [{'uptime': '2019-01-25 12:18:42', 'duration': 0.0, 'downtime': '2019-01-25 12:18:42'}, {'uptime': '2019-01-31 05:20:06', 'duration': 4.0, 'downtime': '2019-01-31 05:20:02'}, {'uptime': '2019-01-26 11:31:28', 'duration': 316.0, 'downtime': '2019-01-26 11:26:12'}, {'uptime': '2019-01-29 09:01:47', 'duration': 62.0, 'downtime': '2019-01-29 09:00:45'}, {'uptime': '2019-01-26 11:48:07', 'duration': 0.0, 'downtime': '2019-01-26 11:48:07'}], 'flash': 2, 'ratio': 99.99}
