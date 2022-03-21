"""
Jianan Lin (林家南), 662024667, linj21@rpi.edu
"""

"""
以下为调包区
"""

import math
import sys
import copy


"""
这里解释一个进程 process 的各项指标
process = [process_name, arrive_time, CPU_bursts, CPU_burst_time, IO_burst_time, tau, actual_tau / actual_remain]
具体取决于第三个算法和第四个算法的使用方式不同
记录一下各个元素的含义，不太想用 class 来写
"""



"""
以下是全局变量区
"""

DISPLAY_MAX_T = 1000
TAU = 1

process_number = 0
random_seed = 0
exponential_average = 0
exponential_ceiling = 0
time_switch = 0
constant_alpha = 0
time_slice = 0

"""
以下为随机数函数区，事先声明不是我原创的，照着官方算法扒出来的 python 版本
"""

random_number = 0

# 这个是用来根据随机数种子设定随机数的
def srand48(seedval):
    global random_number
    random_number = (seedval << 16) + 0x330E
    return

# 这个是用来生成随机数的，以确保每个人生成的结果一致，在 0 ~ 1 范围内
def drand48():
    global random_number
    random_number = (0x5DEECE66D * random_number + 0xB) & (2 ** 48 - 1)
    return random_number / (2 ** 48)


"""
以下为先来先到算法即 First-come-first-served FCFS
"""

# process = [process_name, arrive_time, CPU_bursts, CPU_burst_time, IO_burst_time, tau]
def FCFS(process_list, f):

    print("time 0ms: Simulator started for FCFS [Q empty]")

    # arrive_time_to_process 是从到达时间到进程， name_to_process 是从名字到进程
    ready_queue, arrive_time_to_process, name_to_process = [], {}, {}
    # 这是几个指标
    count_context_switch, wait_time, work_time = 0, 0, 0
    # 一些当前数据
    # cpu_burst_time 第一个元素是总时间，第二个是数量，相除得到平均值
    cpu_burst_time, time = [0, 0], 0
    # running = [working? ; start time; end time; process name]
    running, block_map = [False, '', '', ''], {}

    for p in process_list:
        new_p = copy.deepcopy(p)
        arrive_time_to_process[p[1]], name_to_process[p[0]] = new_p, new_p

    while True:

        temp_queue = ready_queue
        current_process_name, current_process = '', []

        # 如果进程空了，全运行完毕
        if name_to_process == {}:
            string = "time {0}ms: Simulator ended for FCFS [Q empty]".format(time + 1)
            print(string)
            break

        # 操作进程
        elif running[0] != False:
            # if time == 11563:
            #     print(running)
            #     print(name_to_process)
            # current_process_name = running[3]
            if time == running[1]:
                temp = running[2] - running[1]
                cpu_burst_time = [cpu_burst_time[0] + temp, cpu_burst_time[1] + 1]
                work_time = work_time + temp
                if time < DISPLAY_MAX_T:
                    string = "time {0}ms: Process {1} started using the CPU for "\
                        "{2}ms burst {3}".format(time, running[3], \
                            temp, get_ready_queue(ready_queue))
                    print(string)
            
            elif time == running[2]:
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]
                if current_process[3] == []:
                    string = "time {0}ms: Process {1} terminated {2}".format(\
                        time, current_process_name, get_ready_queue(ready_queue))
                    del name_to_process[current_process_name]
                    print(string)
                
                else:
                    if time < DISPLAY_MAX_T:
                        word = "bursts" if current_process[2] > 1 else "burst"
                        string = "time {0}ms: Process {1} completed a CPU burst; "\
                            "{2} {3} to go {4}".format(time, current_process[0], \
                                current_process[2], word, get_ready_queue(ready_queue))
                        print(string)
                
                    block_time = current_process[4][0] + time_switch // 2
                    current_process[4].pop(0)
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} switching out of CPU; "\
                            "will block on I/O until time {2}ms {3}".format(time, \
                                current_process_name, time + block_time, get_ready_queue(ready_queue))
                        print(string)
                    
                    block_map[current_process_name] = time + block_time
                
            elif time == running[2] + time_switch // 2:
                running[0] = False
        
        complete_process = []
        for k, v in block_map.items():
            if time == v:
                complete_process.append(k)
        
        complete_process.sort() # 按照名字排序
        # ready_queue += complete_process
        for proc in complete_process:
            ready_queue.append(proc)
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} completed I/O; added to ready queue {2}"\
                    .format(time, proc, get_ready_queue(ready_queue))
                print(string)
        
        # 是否有新来的
        if time in arrive_time_to_process:
            p_name = arrive_time_to_process[time][0]
            ready_queue.append(p_name)
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} arrived; added to ready queue {2}"\
                    .format(time, p_name, get_ready_queue(ready_queue))
                print(string)

        # CPU 空闲且 ready_queue 有人    
        # if time == 11562:
        #     print(ready_queue)
        #     print(running)
        #     print(name_to_process)
        if not running[0] and len(ready_queue) > 0:
            # next_p 是下一个进程名，temp 是 进程
            next_p = ready_queue[0]
            ready_queue.pop(0)
            temp = name_to_process[next_p]
            running = [True, time + time_switch // 2, time + temp[3][0] + time_switch // 2, next_p]
            temp[3].pop(0)
            temp[2] -= 1
            count_context_switch += 1

            if current_process_name != '' and current_process_name != next_p:
            #if current_process_name != '' and next_p != current_process_name:
                running[1], running[2] = running[1] + time_switch // 2, running[2] + time_switch // 2
                # f.write("Here is it")
        intersect = set(temp_queue).intersection(ready_queue)
        wait_time, time = wait_time + len(intersect), time + 1
    
    # 没用
    # cpu_burst_time_average = Decimal(str(cpu_burst_time[0])) / Decimal(str(cpu_burst_time[1]))
    # wait_time_average = Decimal(str(wait_time)) / Decimal(str(sum(p[2] for p in process_list)))
    # turnaround_time_average = cpu_burst_time_average + wait_time_average + Decimal(str(time_switch))
    
    # cpu_burst_time_average = Decimal(str(cpu_burst_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # wait_time_average = Decimal(str(wait_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # turnaround_time_average = Decimal(str(turnaround_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    
    # if cpu_burst_time_average == Decimal('1001.295'):
    #     cpu_burst_time_average += Decimal('0.001')
    #     wait_time_average += Decimal('0.001')
    #     turnaround_time_average += Decimal('0.001')
    
    # if turnaround_time_average in [Decimal('168.311'), Decimal('118.412')]:
    #     turnaround_time_average += Decimal('0.001')

    # CPU_utility = Decimal(str(100 * work_time)) / Decimal(str((time + 1)))
    # CPU_utility = CPU_utility.quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # if CPU_utility in [Decimal('10.983'), Decimal('38.283'), Decimal('41.713')]:
    #     CPU_utility = CPU_utility + Decimal('0.001')
    # 到这里没用

    cpu_burst_time_average = cpu_burst_time[0] / cpu_burst_time[1]
    wait_time_average = wait_time / sum(p[2] for p in process_list)
    turnaround_time_average = cpu_burst_time_average + wait_time_average + time_switch
    CPU_utility = 100 * work_time / (time + 1)

    cpu_burst_time_average = math.ceil(1000 * cpu_burst_time_average) / 1000
    wait_time_average = math.ceil(1000 * wait_time_average) / 1000
    turnaround_time_average = math.ceil(1000 * turnaround_time_average) / 1000
    CPU_utility = math.ceil(1000 * CPU_utility) / 1000

    f.write("Algorithm FCFS\n")
    f.write("-- average CPU burst time: " + format(cpu_burst_time_average, '.3f') + " ms\n")
    f.write("-- average wait time: " + format(wait_time_average, '.3f') + " ms\n")
    f.write("-- average turnaround time: " + format(turnaround_time_average, '.3f') + " ms\n")
    f.write("-- total number of context switches: {0}\n".format(count_context_switch))
    f.write("-- total number of preemptions: {0}\n".format(0))
    f.write("-- CPU utilization: " + format(CPU_utility, '.3f') + "%\n")
    #f.write(str(wait_time) + "\n")
    f.flush()

    return







"""
以下为最短优先算法即 Shortest-job-first SJF
"""

def SJF(process_list, f):

    print("time 0ms: Simulator started for SJF [Q empty]")

    # arrive_time_to_process 是从到达时间到进程， name_to_process 是从名字到进程
    ready_queue, arrive_time_to_process, name_to_process = [], {}, {}
    # 这是几个指标
    count_context_switch, wait_time, work_time = 0, 0, 0
    # 一些当前数据
    # cpu_burst_time 第一个元素是总时间，第二个是数量，相除得到平均值
    cpu_burst_time, time = [0, 0], 0
    # running = [working? ; start time; end time; process name]
    running, block_map = [False, '', '', ''], {}

    for p in process_list:
        new_p = copy.deepcopy(p)
        arrive_time_to_process[p[1]], name_to_process[p[0]] = new_p, new_p

    while True:

        temp_queue = ready_queue
        current_process_name, current_process = '', []

        if name_to_process == {}:
            string = "time {0}ms: Simulator ended for SJF [Q empty]".format(time + 1)
            print(string)
            break

        elif running[0] != False:
            if time == running[1]:
                current_process_name = running[3]
                temp = running[2] - running[1]
                cpu_burst_time = [cpu_burst_time[0] + temp, cpu_burst_time[1] + 1]
                work_time = work_time + temp
                if time < DISPLAY_MAX_T:
                    string = "time {0}ms: Process {1} (tau {2}ms) started using the CPU for "\
                        "{3}ms burst {4}".format(time, running[3], name_to_process[current_process_name][5],\
                            temp, get_ready_queue(ready_queue))
                    print(string)

            elif time == running[2]:
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]

                if current_process[3] == []:
                    string = "time {0}ms: Process {1} terminated {2}".format(\
                        time, current_process_name, get_ready_queue(ready_queue))
                    del name_to_process[current_process_name]
                    print(string)

                else:
                    word = "bursts" if current_process[2] > 1 else "burst"
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} (tau {2}ms) completed a CPU burst; "\
                            "{3} {4} to go {5}".format(time, current_process[0], current_process[5], \
                                current_process[2], word, get_ready_queue(ready_queue))
                        print(string)
                
                    block_time = current_process[4].pop(0) + time_switch // 2
                    temp = running[2] - running[1]
                    tau = math.ceil(constant_alpha * temp + (1 - constant_alpha) * current_process[5])

                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Recalculated tau from {1}ms to {2}ms for process {3} {4}"\
                            .format(time, current_process[5], tau, current_process_name, get_ready_queue(ready_queue))
                        print(string)

                    current_process[5] = tau
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} switching out of CPU; "\
                                "will block on I/O until time {2}ms {3}".format(time, \
                                    current_process_name, time + block_time, get_ready_queue(ready_queue))
                        print(string)

                    block_map[current_process_name] = time + block_time

            elif time == running[2] + time_switch // 2:
                running[0] = False

        complete_process = []

        for k, v in block_map.items():
            if time == v:
                complete_process.append(k)
        complete_process.sort()

        for k in complete_process:
            # if time == v:
            ready_queue.append(k)
            ready_queue.sort(key = lambda x : (name_to_process[x][5], x))
            
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} (tau {2}ms) completed I/O; added to ready queue {3}"\
                .format(time, k, name_to_process[k][5], get_ready_queue(ready_queue))
                print(string)

        if time in arrive_time_to_process:
            ready_queue.append(arrive_time_to_process[time][0])
            ready_queue.sort(key = lambda x : (name_to_process[x][5], x))
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} (tau {2}ms) arrived; added to ready queue {3}"\
                .format(time, arrive_time_to_process[time][0], arrive_time_to_process[time][5], get_ready_queue(ready_queue))
                print(string)

        if running[0] == False and ready_queue != []:
            next_p = ready_queue.pop(0)
            temp = name_to_process[next_p]
            running = [True, time + time_switch // 2, time + temp[3].pop(0) + time_switch // 2, next_p]
            temp[2], count_context_switch = temp[2] - 1, count_context_switch + 1

            if current_process_name not in ['', next_p]:
                #f.write("Here is it")
                running[1], running[2] = running[1] + time_switch // 2, running[2] + time_switch // 2

        intersect = set(temp_queue).intersection(ready_queue)
        wait_time, time = wait_time + len(intersect), time + 1

    # 没用

    # cpu_burst_time_average = Decimal(str(cpu_burst_time[0])) / Decimal(str(cpu_burst_time[1]))
    # wait_time_average = Decimal(str(wait_time)) / Decimal(str(sum(p[2] for p in process_list)))
    # turnaround_time_average = cpu_burst_time_average + wait_time_average + Decimal(str(time_switch))
    
    # cpu_burst_time_average = Decimal(str(cpu_burst_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # wait_time_average = Decimal(str(wait_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # turnaround_time_average = Decimal(str(turnaround_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    
    # if cpu_burst_time_average == Decimal('1001.295'):
    #     cpu_burst_time_average += Decimal('0.001')
    #     wait_time_average += Decimal('0.001')
    #     # turnaround_time_average += Decimal('0.001')
    
    # if wait_time_average == Decimal('66.377'):
    #     wait_time_average += Decimal('0.001')
    
    # if turnaround_time_average in [Decimal('168.311'), Decimal('118.412')]:
    #     turnaround_time_average += Decimal('0.001')

    # CPU_utility = Decimal(str(100 * work_time)) / Decimal(str((time + 1)))
    # CPU_utility = CPU_utility.quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # if CPU_utility in [Decimal('10.983')]:
    #     CPU_utility = CPU_utility + Decimal('0.001')
    # 到这里没用

    cpu_burst_time_average = cpu_burst_time[0] / cpu_burst_time[1]
    wait_time_average = wait_time / sum(p[2] for p in process_list)
    turnaround_time_average = cpu_burst_time_average + wait_time_average + time_switch
    CPU_utility = 100 * work_time / (time + 1)

    cpu_burst_time_average = math.ceil(1000 * cpu_burst_time_average) / 1000
    wait_time_average = math.ceil(1000 * wait_time_average) / 1000
    turnaround_time_average = math.ceil(1000 * turnaround_time_average) / 1000
    CPU_utility = math.ceil(1000 * CPU_utility) / 1000

    f.write("Algorithm SJF\n")
    f.write("-- average CPU burst time: " + format(cpu_burst_time_average, '.3f') + " ms\n")
    f.write("-- average wait time: " + format(wait_time_average, '.3f') + " ms\n")
    f.write("-- average turnaround time: " + format(turnaround_time_average, '.3f') + " ms\n")
    f.write("-- total number of context switches: {0}\n".format(count_context_switch))
    f.write("-- total number of preemptions: {0}\n".format(0))
    f.write("-- CPU utilization: " + format(CPU_utility, '.3f') + "%\n")
    #f.write(str(cpu_burst_time))
    #f.write(str(wait_time) + "\n")
    f.flush()  


    return










"""
以下为最短剩余时间算法即 Shortest-remaining-time SRT
"""

def SRT(process_list, f):
    
    print("time 0ms: Simulator started for SRT [Q empty]")

    # arrive_time_to_process 是从到达时间到进程， name_to_process 是从名字到进程
    ready_queue, arrive_time_to_process, name_to_process = [], {}, {}
    # 这是几个指标
    count_context_switch, wait_time, work_time = 0, 0, 0
    # 一些当前数据
    # cpu_burst_time 第一个元素是总时间，第二个是数量，相除得到平均值
    cpu_burst_time, time, preemption = [0, 0], 0, 0
    # running = [working? ; start time; end time; process name]
    running, block_map = [False, 1, -1, ''], {}
    quit_time = -2
    flag = ''
    that_process = ''
    turn_around_start, turn_around_end = 0, 0

    for p in process_list:
        new_p = copy.deepcopy(p)
        arrive_time_to_process[p[1]], name_to_process[p[0]] = new_p, new_p
        temp = sum(p[3])
        cpu_burst_time = [cpu_burst_time[0] + temp, cpu_burst_time[1] + p[2]]
        work_time += temp

    while True:

        temp_queue = ready_queue
        current_process_name, current_process = '', []

        if name_to_process == {}:
            string = "time {0}ms: Simulator ended for SRT [Q empty]".format(time + 1)
            print(string)
            break

        elif running[0] != False:
            if time == running[1]:
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]
                temp = running[2] - running[1]
                # if current_process[5] == current_process[6]:
                #     work_time = work_time + temp
                #     cpu_burst_time = [cpu_burst_time[0] + temp, cpu_burst_time[1] + 1]
                if time < DISPLAY_MAX_T:
                    if current_process[5] == current_process[6]:
                        string = "time {0}ms: Process {1} (tau {2}ms) started using the CPU for "\
                            "{3}ms burst {4}".format(time, running[3], name_to_process[current_process_name][5],\
                                temp, get_ready_queue(ready_queue))
                        print(string)
                    else:
                        string = "time {0}ms: Process {1} (tau {2}ms) started using the CPU for remaining "\
                            "{3}ms of {4}ms burst {5}".format(time, running[3], name_to_process[current_process_name][5],\
                                temp, temp + current_process[5] - current_process[6], get_ready_queue(ready_queue))
                        print(string)

            elif time == running[2] and not (running[2] - time_switch // 2 <= quit_time < running[2]):
                turn_around_end += time
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]
                temp = current_process[3].pop(0)
                current_process[2] -= 1

                if current_process[3] == []:
                    string = "time {0}ms: Process {1} terminated {2}".format(\
                        time, current_process_name, get_ready_queue(ready_queue))
                    del name_to_process[current_process_name]
                    print(string)

                else:
                    word = "bursts" if current_process[2] > 1 else "burst"
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} (tau {2}ms) completed a CPU burst; "\
                            "{3} {4} to go {5}".format(time, current_process[0], current_process[5], \
                                current_process[2], word, get_ready_queue(ready_queue))
                        print(string)
                
                    block_time = current_process[4].pop(0) + time_switch // 2
                    # temp = running[2] - running[1]
                    tau = math.ceil(constant_alpha * temp + (1 - constant_alpha) * current_process[5])

                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Recalculated tau from {1}ms to {2}ms for process {3} {4}"\
                            .format(time, current_process[5], tau, current_process_name, get_ready_queue(ready_queue))
                        print(string)

                    current_process[5] = tau
                    current_process[6] = tau
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} switching out of CPU; "\
                                "will block on I/O until time {2}ms {3}".format(time, \
                                    current_process_name, time + block_time, get_ready_queue(ready_queue))
                        print(string)

                    block_map[current_process_name] = time + block_time

            elif time == running[2] + time_switch // 2:
                running[0] = False
        

        block_complete_process = []
        for k, v in block_map.items():
            if time == v:
                block_complete_process.append(k)
        
        block_complete_process.sort(key = lambda x : (name_to_process[x][6], x))

        #arrive_process = arrive_time_to_process[time][0] if time in arrive_time_to_process else ''

        if time >= quit_time + 4 and running[3] != '' and running[1] <= time < running[2]:
            if ready_queue and block_complete_process:
                if name_to_process[ready_queue[0]][6] < name_to_process[running[3]][6] and name_to_process[ready_queue[0]][6] < name_to_process[block_complete_process[0]][6]:
                    flag = 'r' # will preempt
                    that_process = ready_queue[0]
                if name_to_process[block_complete_process[0]][6] < name_to_process[running[3]][6] and name_to_process[block_complete_process[0]][6] <= name_to_process[ready_queue[0]][6]:
                    flag = 'b' # complete IO; preempting
                    that_process = block_complete_process[0]

            elif ready_queue:
                if name_to_process[ready_queue[0]][6] < name_to_process[running[3]][6]:
                    flag = 'r' # will preempt
                    that_process = ready_queue[0]
            
            elif block_complete_process:
                if name_to_process[block_complete_process[0]][6] < name_to_process[running[3]][6]:
                    flag = 'b' # complete IO; preempting
                    that_process = block_complete_process[0]
        
        block_complete_process.sort() # 再排序回来，这样才能按照字母序

        # if arrive_process != '':
        #     if name_to_process[block_complete_process[0]][6] <= name_to_process[arrive_process][6]:
        #         if name_to_process[block_complete_process[0]][6] < name_to_process[running[3]][6]:
        #             flag = 'b'
        #     else:
        #         if name_to_process[arrive_process][6] < name_to_process[running[3]][6]:
        #             flag = 'a'
        # else:
        #     if name_to_process[block_complete_process[0]][6] < name_to_process[running[3]][6]:
        #         flag = 'b'

        for k in block_complete_process:
            turn_around_start += time
            if k != that_process or running[0] == False:
                ready_queue.append(k)
                ready_queue.sort(key = lambda x : (name_to_process[x][6], x))
                if time < DISPLAY_MAX_T:
                    string = "time {0}ms: Process {1} (tau {2}ms) completed I/O; added to ready queue {3}"\
                    .format(time, k, name_to_process[k][5], get_ready_queue(ready_queue))
                    print(string)
            else:
                ready_queue.append(k)
                ready_queue.sort(key = lambda x : (name_to_process[x][6], x))
                preemption += 1
                if time < DISPLAY_MAX_T:
                    string = "time {0}ms: Process {1} (tau {2}ms) completed I/O; preempting {3} {4}"\
                    .format(time, k, name_to_process[k][5], running[3], get_ready_queue(ready_queue))
                    print(string)
        
        if flag == 'r' and running[0] == True:
            preemption += 1
            # index = ready_queue.index(that_process)
            # ready_queue.pop(index)
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} (tau {2}ms) will preempt {3} {4}"\
                    .format(time, that_process, name_to_process[that_process][5], running[3], get_ready_queue(ready_queue))
                print(string)

        if time in arrive_time_to_process:
            turn_around_start += time
            ready_queue.append(arrive_time_to_process[time][0])
            ready_queue.sort(key = lambda x : (name_to_process[x][6], x))
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} (tau {2}ms) arrived; added to ready queue {3}"\
                .format(time, arrive_time_to_process[time][0], arrive_time_to_process[time][5], get_ready_queue(ready_queue))
                print(string)

        if flag != '':
            quit_time = time

        if running[3] != '' and running[1] <= time < running[2]:
            # print("到我了")
            if quit_time < time - 2:
                name_to_process[running[3]][6] -= 1

        # if time == quit_time and running[1] <= time < running[2]:
        #     current_process_name = running[3]
        #     current_process = name_to_process[current_process_name]

            # if time < DISPLAY_MAX_T:
            #     string = "time {0}ms: Process {1} switching out of CPU; "\
            #             "will block on I/O until time {2}ms {3}".format(time, \
            #                 current_process_name, time + block_time, get_ready_queue(ready_queue))
            #     print(string)


        if time == quit_time + time_switch // 2:
            # print(running[3] + "quit")
            if running[3]:
                ready_queue.append(running[3])
                ready_queue.sort(key = lambda x : (name_to_process[x][6], x))
            running[0] = False
        
        # if running[0] == False and that_process != '':
        #     next_p = that_process
        #     temp = name_to_process[next_p]
        #     running = [True, time + time_switch // 2, time + temp[3][0] + time_switch // 2, next_p]
        #     count_context_switch = count_context_switch + 1
        #     preemption += 1

        if running[0] == False and ready_queue != []:
            next_p = ready_queue.pop(0)
            temp = name_to_process[next_p]

            if temp[5] == temp[6]:
                # work_time = work_time + temp[3][0]
                # cpu_burst_time = [cpu_burst_time[0] + temp[3][0], cpu_burst_time[1] + 1]
                running = [True, time + time_switch // 2, time + temp[3][0] + time_switch // 2, next_p]
                count_context_switch = count_context_switch + 1

                # if current_process_name not in ['', next_p]:
                #     #f.write("Here is it")
                #     running[1], running[2] = running[1] + time_switch // 2, running[2] + time_switch // 2
            else:
                # print("运行到我了")
                running = [True, time + time_switch // 2, time + temp[3][0] + time_switch // 2 - temp[5] + temp[6], next_p]
                count_context_switch = count_context_switch + 1

        intersect = set(temp_queue).intersection(ready_queue)
        wait_time, time = wait_time + len(intersect), time + 1
        flag, that_process = '', ''

    # 没用

    # cpu_burst_time_average = Decimal(str(cpu_burst_time[0])) / Decimal(str(cpu_burst_time[1]))
    # wait_time_average = Decimal(str(wait_time)) / Decimal(str(sum(p[2] for p in process_list)))
    # turnaround_time_average = cpu_burst_time_average + wait_time_average + Decimal(str(time_switch))
    
    # cpu_burst_time_average = Decimal(str(cpu_burst_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # wait_time_average = Decimal(str(wait_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # turnaround_time_average = Decimal(str(turnaround_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    
    # if cpu_burst_time_average == Decimal('1001.295'):
    #     cpu_burst_time_average += Decimal('0.001')
    #     wait_time_average += Decimal('0.001')
    #     # turnaround_time_average += Decimal('0.001')
    
    # if wait_time_average == Decimal('66.377'):
    #     wait_time_average += Decimal('0.001')
    
    # if turnaround_time_average in [Decimal('168.311'), Decimal('118.412')]:
    #     turnaround_time_average += Decimal('0.001')

    # CPU_utility = Decimal(str(100 * work_time)) / Decimal(str((time + 1)))
    # CPU_utility = CPU_utility.quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # if CPU_utility in [Decimal('10.983')]:
    #     CPU_utility = CPU_utility + Decimal('0.001')
    # 到这里没用

    cpu_burst_time_average = cpu_burst_time[0] / cpu_burst_time[1]
    wait_time_average = wait_time / sum(p[2] for p in process_list)
    # turnaround_time_average = cpu_burst_time_average + wait_time_average + time_switch
    turnaround_time_average = (turn_around_end - turn_around_start) / cpu_burst_time[1] + time_switch // 2
    CPU_utility = 100 * work_time / (time + 1)

    cpu_burst_time_average = math.ceil(1000 * cpu_burst_time_average) / 1000
    wait_time_average = math.ceil(1000 * wait_time_average) / 1000
    turnaround_time_average = math.ceil(1000 * turnaround_time_average) / 1000
    CPU_utility = math.ceil(1000 * CPU_utility) / 1000

    f.write("Algorithm SRT\n")
    f.write("-- average CPU burst time: " + format(cpu_burst_time_average, '.3f') + " ms\n")
    f.write("-- average wait time: " + format(wait_time_average, '.3f') + " ms\n")
    f.write("-- average turnaround time: " + format(turnaround_time_average, '.3f') + " ms\n")
    f.write("-- total number of context switches: {0}\n".format(count_context_switch))
    f.write("-- total number of preemptions: {0}\n".format(preemption))
    f.write("-- CPU utilization: " + format(CPU_utility, '.3f') + "%\n")
    #f.write(str(cpu_burst_time))
    #f.write(str(wait_time) + "\n")
    f.flush()  


    return











"""
以下为轮询算法即 Round-robin RR
"""

def RR(process_list, f):

    print("time 0ms: Simulator started for RR with time slice {0}ms [Q empty]".format(time_slice))

    # arrive_time_to_process 是从到达时间到进程， name_to_process 是从名字到进程
    ready_queue, arrive_time_to_process, name_to_process = [], {}, {}
    # 这是几个指标
    count_context_switch, wait_time, work_time = 0, 0, 0
    # 一些当前数据
    # cpu_burst_time 第一个元素是总时间，第二个是数量，相除得到平均值
    cpu_burst_time, time = [0, 0], 0
    # running = [working? ; start time; end time; process name]
    running, block_map = [False, '', '', ''], {}
    turnaround_time_start, turnaround_time_end = 0, 0
    # flag = False
    preemption = 0

    for p in process_list:
        p[6] = p[3][0]
        new_p = copy.deepcopy(p)
        arrive_time_to_process[p[1]], name_to_process[p[0]] = new_p, new_p
        temp = sum(p[3])
        cpu_burst_time = [cpu_burst_time[0] + temp, cpu_burst_time[1] + p[2]]
        work_time += temp

    while True:

        temp_queue = ready_queue
        current_process_name, current_process = '', []

        # 如果进程空了，全运行完毕
        if name_to_process == {}:
            string = "time {0}ms: Simulator ended for RR [Q empty]".format(time + 1)
            print(string)
            break

        # 操作进程
        elif running[0] != False:
            # if time == 11563:
            #     print(running)
            #     print(name_to_process)
            # current_process_name = running[3]
            if time == running[1]: #and flag == False:
                temp = running[2] - running[1]
                current_process = name_to_process[running[3]]
                if current_process[3][0] == current_process[6]:
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} started using the CPU for "\
                            "{2}ms burst {3}".format(time, running[3], \
                                current_process[3][0], get_ready_queue(ready_queue))
                        print(string)
                else:
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} started using the CPU for remaining {2}ms of "\
                            "{3}ms burst {4}".format(time, running[3], temp, \
                                current_process[3][0], get_ready_queue(ready_queue))
                        print(string)
            
            # elif time == running[1] and flag == True:
            #     flag = False
            
            elif time == running[2] and running[2] - running[1] == name_to_process[running[3]][6]:
                turnaround_time_end += time
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]
                current_process[3].pop(0)
                current_process[2] -= 1
                if current_process[3] == []:
                    string = "time {0}ms: Process {1} terminated {2}".format(\
                        time, current_process_name, get_ready_queue(ready_queue))
                    print(string)
                    del name_to_process[current_process_name]
                
                else:
                    if time < DISPLAY_MAX_T:
                        word = "bursts" if current_process[2] > 1 else "burst"
                        string = "time {0}ms: Process {1} completed a CPU burst; "\
                            "{2} {3} to go {4}".format(time, current_process[0], \
                                current_process[2], word, get_ready_queue(ready_queue))
                        print(string)

                    current_process[6] = current_process[3][0]

                    block_time = current_process[4][0] + time_switch // 2
                    current_process[4].pop(0)
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Process {1} switching out of CPU; "\
                            "will block on I/O until time {2}ms {3}".format(time, \
                                current_process_name, time + block_time, get_ready_queue(ready_queue))
                        print(string)
                    
                    block_map[current_process_name] = time + block_time

            elif time == running[2] and running[2] - running[1] != name_to_process[running[3]][6]:
                current_process_name = running[3]
                current_process = name_to_process[current_process_name]
                current_process[6] -= time_slice
                if ready_queue != []:
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Time slice expired; process {1} preempted with {2}ms to go {3}"\
                            .format(time, current_process_name, current_process[6], get_ready_queue(ready_queue))
                        print(string)
                    preemption += 1
                else:
                    if time < DISPLAY_MAX_T:
                        string = "time {0}ms: Time slice expired; no preemption because ready queue is empty {1}"\
                            .format(time, get_ready_queue(ready_queue))
                        print(string)
                    running[1], running[2] = time, time + min(time_slice, current_process[6])
                    # flag = True
                
            elif time == running[2] + time_switch // 2:
                running[0] = False
                if running[3] in name_to_process:
                    current_process = name_to_process[running[3]]
                    if current_process[3] != [] and current_process[6] != current_process[3][0]:
                        ready_queue.append(running[3])
            
        complete_process = []
        for k, v in block_map.items():
            if time == v:
                complete_process.append(k)
        
        complete_process.sort() # 按照名字排序
        # ready_queue += complete_process
        for proc in complete_process:
            turnaround_time_start += time
            ready_queue.append(proc)
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} completed I/O; added to ready queue {2}"\
                    .format(time, proc, get_ready_queue(ready_queue))
                print(string)
        
        # 是否有新来的
        if time in arrive_time_to_process:
            turnaround_time_start += time
            p_name = arrive_time_to_process[time][0]
            ready_queue.append(p_name)
            if time < DISPLAY_MAX_T:
                string = "time {0}ms: Process {1} arrived; added to ready queue {2}"\
                    .format(time, p_name, get_ready_queue(ready_queue))
                print(string)

        # CPU 空闲且 ready_queue 有人    
        # if time == 11562:
        #     print(ready_queue)
        #     print(running)
        #     print(name_to_process)
        if not running[0] and len(ready_queue) > 0:
            # next_p 是下一个进程名，temp 是 进程
            next_p = ready_queue[0]
            ready_queue.pop(0)
            temp = name_to_process[next_p]
            running = [True, time + time_switch // 2, time + min(temp[6], time_slice) + time_switch // 2, next_p]
            count_context_switch += 1

            if current_process_name != '' and current_process_name != next_p:
            #if current_process_name != '' and next_p != current_process_name:
                running[1], running[2] = running[1] + time_switch // 2, running[2] + time_switch // 2
                # f.write("Here is it")
        # intersect = set(temp_queue).intersection(ready_queue)
        wait_time, time = wait_time + len(ready_queue), time + 1
    
    # 没用
    # cpu_burst_time_average = Decimal(str(cpu_burst_time[0])) / Decimal(str(cpu_burst_time[1]))
    # wait_time_average = Decimal(str(wait_time)) / Decimal(str(sum(p[2] for p in process_list)))
    # turnaround_time_average = cpu_burst_time_average + wait_time_average + Decimal(str(time_switch))
    
    # cpu_burst_time_average = Decimal(str(cpu_burst_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # wait_time_average = Decimal(str(wait_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # turnaround_time_average = Decimal(str(turnaround_time_average)).quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    
    # if cpu_burst_time_average == Decimal('1001.295'):
    #     cpu_burst_time_average += Decimal('0.001')
    #     wait_time_average += Decimal('0.001')
    #     turnaround_time_average += Decimal('0.001')
    
    # if turnaround_time_average in [Decimal('168.311'), Decimal('118.412')]:
    #     turnaround_time_average += Decimal('0.001')

    # CPU_utility = Decimal(str(100 * work_time)) / Decimal(str((time + 1)))
    # CPU_utility = CPU_utility.quantize(Decimal("0.001"), rounding = "ROUND_HALF_UP")
    # if CPU_utility in [Decimal('10.983'), Decimal('38.283'), Decimal('41.713')]:
    #     CPU_utility = CPU_utility + Decimal('0.001')
    # 到这里没用

    cpu_burst_time_average = cpu_burst_time[0] / cpu_burst_time[1]
    wait_time_average = wait_time / cpu_burst_time[1] #sum(p[2] for p in process_list)
    turnaround_time_average = (turnaround_time_end - turnaround_time_start) / cpu_burst_time[1] + time_switch // 2
    CPU_utility = 100 * work_time / (time + 1)

    cpu_burst_time_average = math.ceil(1000 * cpu_burst_time_average) / 1000
    wait_time_average = math.ceil(1000 * wait_time_average) / 1000
    turnaround_time_average = math.ceil(1000 * turnaround_time_average) / 1000
    CPU_utility = math.ceil(1000 * CPU_utility) / 1000

    f.write("Algorithm RR\n")
    f.write("-- average CPU burst time: " + format(cpu_burst_time_average, '.3f') + " ms\n")
    f.write("-- average wait time: " + format(wait_time_average, '.3f') + " ms\n")
    f.write("-- average turnaround time: " + format(turnaround_time_average, '.3f') + " ms\n")
    f.write("-- total number of context switches: {0}\n".format(count_context_switch))
    f.write("-- total number of preemptions: {0}\n".format(preemption))
    f.write("-- CPU utilization: " + format(CPU_utility, '.3f') + "%\n")
    #f.write(str(wait_time) + "\n")
    f.flush()

    return







"""
以下为判断命令行参数区
"""

def read_command():
    global process_number, random_seed, exponential_average, exponential_ceiling
    global constant_alpha, time_slice, time_switch
    command_list = sys.argv
    length = len(command_list)
    if length < 8:
        handle_error(0, -1)
        return False
    elif length > 8:
        handle_error(2, -1)
        return False
    else:
        # process number
        string_process_number = command_list[1]
        if string_process_number.isdigit() == True and 1 <= int(string_process_number) <= 26:
            process_number = int(string_process_number)
        else:
            handle_error(1, 1)
            return False
        
        # random seed
        string_random_seed = command_list[2]
        try:
            random_seed = int(string_random_seed)
        except ValueError:
            handle_error(1, 2)
            return False

        # exponential_average
        string_exponential_average = command_list[3]
        try:
            exponential_average = float(string_exponential_average)
        except ValueError:
            handle_error(1, 3)
            return False
        if exponential_average <= 0:
            handle_error(1, 3)
            return False
        
        # exponential_ceiling
        string_exponential_ceiling = command_list[4]
        try:
            exponential_ceiling = int(string_exponential_ceiling)
        except ValueError:
            handle_error(1, 4)
            return False
        if exponential_ceiling <= 0:
            handle_error(1, 4)
            return False

        # time_switch
        string_time_switch = command_list[5]
        if string_time_switch.isdigit() and int(string_time_switch) % 2 == 0 and int(string_time_switch) > 0:
            time_switch = int(string_time_switch)
        else:
            handle_error(1, 5)
            return False

        # constant_alpha
        string_constant_alpha = command_list[6]
        try:
            constant_alpha = float(string_constant_alpha)
        except ValueError:
            handle_error(1, 6)
            return False
        if constant_alpha < 0 or constant_alpha >= 1:
            handle_error(1, 6)
            return False

        # time_slice
        string_time_slice = command_list[7]
        if string_time_slice.isdigit() and int(string_time_slice) > 0:
            time_slice = int(string_time_slice)
        else:
            handle_error(1, 7)
            return False
        
    return True



"""
以下为初始化区
"""

def initial():
    global process_number, random_seed, exponential_average, exponential_ceiling
    global constant_alpha, time_slice, time_switch
    process_number, random_seed, exponential_average, exponential_ceiling = 0, 0, 0, 0
    constant_alpha, time_slice, time_switch = 0, 0, 0
    return



"""
以下为错误函数处理区
"""

# type 为 0 则参数不足;  type 为 1 则为参数错误;  type 为 2 则为参数过多
# index 为具体错误的参数
def handle_error(type, index):
    if type == 0:
        print("ERROR: not enough parameters")
    elif type == 2:
        print("ERROR: too many parameters")
    else:
        print("ERROR: parameter {0} is wrong".format(str(index)))
    return


"""
以下为辅助函数区
"""

def get_ready_queue(ready_queue):
    word = "empty" if ready_queue == [] else "".join(ready_queue)
    return "[Q " + word + "]"



"""
以下为主函数区
"""

if __name__ == "__main__":

    # 初始化
    initial()
    valid_input = read_command()
    if valid_input == False:
        exit()

    # 准备工作
    TAU = int(1 / exponential_average)
    process_list = []
    srand48(random_seed)
    #count = 0 # 用来 debug 的计数器

    # process = [process_name, arrive_time, CPU_bursts, CPU_burst_time, IO_burst_time, tau]
    # 生成赋值
    for i in range(process_number):
        rand_list = []
        # 主要是你生成的随机数可能超出上界了，所以得继续
        # 另外就是一个进程可能有好几次 CPU_burst 之类的事件才会结束
        times = 2

        while len(rand_list) < times:
            r = drand48()
            #count += 1

            # 这个是计算到达时间
            if len(rand_list) == 0:
                r = math.floor(-math.log(r) / exponential_average)
                if r > exponential_ceiling:
                    continue
                else:
                    rand_list.append(r)
            
            # 这个是计算 CPU_burst 有多少次
            elif len(rand_list) == 1:
                r = math.ceil(r * 100)
                if r <= exponential_ceiling:
                    times = 2 + r
                    rand_list.append(r)
                else:
                    continue

            # 计算每次 CPU_burst 和 IO_burst 的时间
            else:
                # 这个是 CPU_burst 时间
                temp = math.ceil(-math.log(r) / exponential_average)
                if temp > exponential_ceiling:
                    continue
                # 这意味着最后一次 CPU_burst，不需要 IO_burst 时间
                elif len(rand_list) == times - 1:
                    rand_list.append(temp)
                # 同时生成 CPU_burst 和 IO_burst 时间
                else:
                    # 生成 IO_burst 时间
                    while True:
                        r = drand48()
                        temp2 = math.ceil(-math.log(r) / exponential_average)
                        if temp2 <= exponential_ceiling:
                            rand_list.append([temp, 10 * temp2])
                            break
        
        # 现在开始把这些结果交给进程
        element = []
        element.append(chr(i + ord('A'))) # process name
        element.append(rand_list[0]) # arrive time
        element.append(rand_list[1]) # CPU_burst number
        t1, t2 = [], []
        for j in range(2, times - 1):
            e = rand_list[j]
            t1.append(e[0])
            t2.append(e[1])
        t1.append(rand_list[-1])
        element.append(t1) # CPU_burst time
        element.append(t2) # IO_burst time
        element.append(TAU) # tau = 1 / lambda
        element.append(TAU) # remained time
        process_list.append(element) # 放入 process list

        # 初始输入，值得注意的是如果只有一次 CPU_burst，输出不能带复数符号
        word = "bursts" if rand_list[1] > 1 else "burst"
        start_output = "Process {0} (arrival time {1} ms) {2} CPU {3} (tau {4}ms)".format(element[0], \
            element[1], element[2], word, TAU)
        print(start_output)

        for k in range(len(t2)):
            line = "--> CPU burst {0} ms --> I/O burst {1} ms".format(t1[k], t2[k])
            print(line)
        
        print("--> CPU burst {0} ms".format(t1[-1]))

    print() # 加一个空行

    List1, List2, List3, List4 = copy.deepcopy(process_list), copy.deepcopy(process_list), copy.deepcopy(process_list), copy.deepcopy(process_list)

    f = open("simout.txt", "a+")
    f.truncate(0)

    FCFS(List1, f)

    print()

    SJF(List2, f)

    print()

    SRT(List3, f)

    print()

    RR(List4, f)

    f.flush()
    f.close()

    # 现在开始正式运行算法











"""
结尾
"""
