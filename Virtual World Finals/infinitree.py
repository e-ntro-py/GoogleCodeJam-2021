# Copyright (c) 2021 kamyu. All rights reserved.
#
# Google Code Jam 2021 Virtual World Finals - Problem E. Infinitree
# https://codingcompetitions.withgoogle.com/codejam/round/0000000000436329/000000000084fc01
#
# Time:  O(N^3.5 * logN + N^3 * logB), pass in PyPy2 but Python2
# Space: O(N^2.5 * logN + N^2 * logB)
#

from itertools import izip

# modified from Template:
# https://github.com/kamyu104/GoogleCodeJam-2018/blob/master/World%20Finals/swordmaster.py
def strongly_connected_components(graph):  # Time: O(|V| + |E|) = O(N + 2N) = O(N), Space: O(|V|) = O(N)
    def strongconnect(v, index_counter, index, lowlinks, stack, stack_set, result):
        index[v] = index_counter[0]
        lowlinks[v] = index_counter[0]
        index_counter[0] += 1
        stack_set.add(v)
        stack.append(v)
        for w in (graph[v] if v in graph else []):
            if w not in index:
                strongconnect(w, index_counter, index, lowlinks, stack, stack_set, result)
                lowlinks[v] = min(lowlinks[v], lowlinks[w])
            elif w in stack_set:
                lowlinks[v] = min(lowlinks[v], index[w])
        if lowlinks[v] == index[v]:
            connected_component = []
            w = None
            while w != v:
                w = stack.pop()
                stack_set.remove(w)
                connected_component.append(w)
            result.append(set(connected_component))

    index_counter, index, lowlinks = [0], {}, {}
    stack, stack_set = [], set()
    result = []
    strongconnect(1, index_counter, index, lowlinks, stack, stack_set, result)  # modified, only care about reachable colors
    return result

def find_cycles(graph):  # Time: O(N), Space: O(N)
    cycle_id = 0
    has_2_up_cycles, cycle_adj, cycle_length = False, {}, {}
    for scc in strongly_connected_components(graph):
        if next(iter(scc)) == 0:
            continue
        if any(sum(int(x in scc) for x in graph[node]) == 2 for node in scc):
            has_2_up_cycles = True
        if any(sum(int(x in scc) for x in graph[node]) != 1 for node in scc):
            continue
        cycle_id += 1
        node = next(iter(scc))
        for node in scc:
            cycle_length[node] = len(scc)
        node = next(iter(scc))
        for _ in xrange(len(scc)):
            cycle_adj[node] = [(x, side, cycle_id) for side, x in enumerate(graph[node]) if x in scc][0]
            cycle_length[node] = len(scc)
            node = cycle_adj[node][0]
    return has_2_up_cycles, cycle_adj, cycle_length

def floor_log2_x(x):  # Time: O(logx)
    return x.bit_length()-1

def identity_matrix(N):  # Time: O(N)
    return [[int(i == j) for j in xrange(N)] for i in xrange(N)]

def e(i, N):  # Time: O(N)
    return [int(j == i) for j in xrange(N)]

def vector_mult(A, B, INF):  # Time: O(N^2), A is a N-d vector, B is a N x N matrix
    result = [0]*len(B[0])
    B_T = zip(*B)
    for i, B_T_i in enumerate(B_T):
        for _, (A_j, B_T_i_j) in enumerate(izip(A, B_T_i)):
            result[i] += A_j*B_T_i_j
            if result[i] > INF:
                result[i] = INF
                break
    return result

def matrix_mult(A, B, INF):  # Time: O(N^3), A, B are both N x N matrixs
    result = [[0]*len(B[0]) for _ in xrange(len(A))]
    B_T = zip(*B)
    for result_i, A_i in izip(result, A):
        for j, B_T_i in enumerate(B_T):
            for A_i_j, B_T_i_j in izip(A_i, B_T_i):
                result_i[j] += A_i_j*B_T_i_j
                if result_i[j] > INF:
                    result_i[j] = INF
                    break
    return result

def vector_add(A, B, INF):  # Time: O(N)
    result = [0]*len(A)
    for i, (A_i, B_i) in enumerate(izip(A, B)):
        result[i] = A_i+B_i
        if result[i] > INF:
            result[i] = INF
    return result

def matrix_add(A, B, INF):  # Time: O(N^2)
    result = [[0]*len(B[0]) for _ in xrange(len(A))]
    for result_i, A_i, B_i in izip(result, A, B):
        for j in xrange(len(result_i)):
            result_i[j] = A_i[j]+B_i[j]
            if result_i[j] > INF:
                result_i[j] = INF
    return result

# build [M, M^2, ..., M^(2^logx)] and [I, (I + M), (I + M + M^2 + M^3), (I + M + ... + M^(2^logx-1))]
def build_powers_and_prefix_powers(N, M, INF, x):  # Time: O(N^3 * logx)
    logx = floor_log2_x(x)
    I = identity_matrix(N)
    # M_powers[i] for i in xrange(1+logx):
    # 0: M
    # 1: M^2
    # ...
    # logx: M^(2^logx)
    M_powers = [M]
    for _ in xrange(logx):  # Time: O(N^3 * logx)
        M_powers.append(matrix_mult(M_powers[-1], M_powers[-1], INF))
    # prefix_M_powers[i] for i in xrange(1+logx):
    # 0: I
    # 1: (I + M) * I = I + M
    # 2: (I + M^2) * (I + M) = I + M + M^2 + M^3
    # ...
    # logx: (I + M^(2^(logx-1))) * (I + M + ... + M^(2^(logx-1)-1)) = I + M + ... + M^(2^logx-1)
    prefix_M_powers = [I]
    for i in xrange(logx):  # Time: O(N^3 * logx)
        matrix = matrix_add(I, M_powers[i], INF)
        prefix_M_powers.append(matrix_mult(matrix, prefix_M_powers[-1], INF))
    return M_powers, prefix_M_powers

# M^x by matrix exponentiation
def get_M_power_x(N, M_powers, INF, x):  # Time: O(N^3 * logx)
    matrix = identity_matrix(N)
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            matrix = matrix_mult(matrix, M_powers[i], INF)
        basis, i = basis<<1, i+1
    return matrix

# v * M^x by vector-matrix exponentiation
def get_v_M_power_x(M_powers, INF, v, x):  # Time: O(N^2 * logx)
    u = v
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            u = vector_mult(u, M_powers[i], INF)  # u*Mi
        basis, i = basis<<1, i+1
    return u

# v * (I + M + M^2 + ... + M^x) by vector-matrix exponentiation
def get_v_sum_M_power_x(N, M_powers, prefix_M_powers, INF, v, x):  # Time: O(N^2 * logx)
    x += 1
    u = [0]*N
    basis, i = 1, 0
    while basis <= x:
        if x&basis:
            # new_Pr = Pi + Pr*Mi
            # new_u = v * new_Pr = v * (Pi + Pr*Mi) = v*Pi + u*Mi
            v1 = vector_mult(u, M_powers[i], INF)  # u*Mi
            v2 = vector_mult(v, prefix_M_powers[i], INF)  # v*Pi
            u = vector_add(v1, v2, INF)  # u*Mi + v*Pi
        basis, i = basis<<1, i+1
    return u

def get_depth(N, M_powers, prefix_M_powers, INF, x):  # Time: O(N^2 * logx)
    logx = floor_log2_x(x)
    result = 0
    e1 = e(1, N)
    u = [0]*N
    basis = 1<<logx
    for i in reversed(xrange(logx+1)):  # O(N^2 * logx)
        # new_Pr = Pi + Pr*Mi
        # new_u = e1 * new_Pr = e1 * (Pi + Pr*Mi) = e1*Pi + u*Mi
        v1 = vector_mult(u, M_powers[i], INF)  # u*Mi
        v2 = vector_mult(e1, prefix_M_powers[i], INF)  # e1*Pi
        new_u = vector_add(v1, v2, INF)  # u*Mi + e1*Pi
        if sum(new_u) < x:
            u = new_u
            result |= basis
        basis >>= 1
    return result

def get_single_step_position(M_powers, INF, ec, h, x):  # Time: O(N^2 * logx)
    left_cnt = sum(get_v_M_power_x(M_powers, INF, ec, h-1))
    return (LEFT, x) if x < left_cnt else (RIGHT, x-left_cnt)

def get_multiple_steps_position(M_powers, prefix_M_H_powers, INF, logp, v, delta_h, ec, x):  # Time: O(N^2 * log(delta_h))
    left_cnt = sum(get_v_M_power_x(M_powers, INF, vector_mult(v, prefix_M_H_powers[logp], INF), delta_h))
    mid_cnt = sum(get_v_M_power_x(M_powers, INF, ec, delta_h))
    return 0 <= x-left_cnt < mid_cnt, x-left_cnt

def infinitree():
    N, A, B = map(int, raw_input().strip().split())
    L = map(int, raw_input().strip().split())
    R = map(int, raw_input().strip().split())
    N += 1
    if A > B:
        A, B, = B, A
    INF = B
    M = [[0]*N for _ in xrange(N)]
    graph = {}
    for i in xrange(1, N):
        M[i][L[i-1]] += 1
        M[i][R[i-1]] += 1
        graph[i] = [L[i-1], R[i-1]]
    M_H_powers, prefix_M_H_powers = {}, {}
    M_H_powers[1], prefix_M_H_powers[1] = build_powers_and_prefix_powers(N, M, INF, B)  # Time: O(N^3 * logB)
    h1 = get_depth(N, M_H_powers[1], prefix_M_H_powers[1], INF, A)
    h2 = get_depth(N, M_H_powers[1], prefix_M_H_powers[1], INF, B)

    has_2_up_cycles, cycle_adj, cycle_length = find_cycles(graph)
    x1 = A-sum(get_v_sum_M_power_x(N, M_H_powers[1], prefix_M_H_powers[1], INF, e(1, N), h1-1))-1
    x2 = B-sum(get_v_sum_M_power_x(N, M_H_powers[1], prefix_M_H_powers[1], INF, e(1, N), h2-1))-1
    c, p  = 1, 0
    while (h1, x1) != (0, 0):
        if has_2_up_cycles or c not in cycle_adj or p == 1:  # enter none-only-1-cycle node, Time: O(N^2 * logB) => Total Time: O(N^2 * (logB)^2)
            side1, new_x1 = get_single_step_position(M_H_powers[1], INF, e(L[c-1], N), h1, x1)
            side2, new_x2 = get_single_step_position(M_H_powers[1], INF, e(L[c-1], N), h2, x2)
            if side1 != side2:  # found lca
                break
            h1, x1 = h1-1, new_x1
            h2, x2 = h2-1, new_x2
            c, prev_c = (L[c-1] if side1 == LEFT else R[c-1]), c
            if p == 1 and (c not in cycle_adj or cycle_adj[c][2] != cycle_adj[prev_c][2]):  # leave prev cycle forever (but may enter other cycles)
                p = 0
            continue
        # path from root to lca enter a new unseen cycle, we can speed up in this part of path,
        # we run this only if all reachable colors belong to at most one cycle,
        # otherwise, the binary tree grows exponentially with height at most O(logB) so that single step solution is fast enough,
        # and also saves the extra time and space cost from multiple steps solution
        h = cycle_length[c]
        if h not in M_H_powers:  # lazy init, sum(distinct h) = N => distinct h at most O(sqrt(N)) times, each Time: O(N^3 * logh + N^3 * log(hi)) => Total Time: O(N^3.5 * logN + (N^3.5 * log(logB) + N^3 * logB)) = O(N^3.5 * logN + N^3 * logB) assumed O(N) = O(logB)
            M_H_powers[h], prefix_M_H_powers[h] = build_powers_and_prefix_powers(N, get_M_power_x(N, M_H_powers[1], INF, h), INF, min(h1, h2))
        v = [0]*N
        for x in reversed(xrange(h)):  # Time: O(h * N^2 * logN) => Total Time O(N^3 * logN)
            if cycle_adj[c][1] and cycle_adj[c][0] == R[c-1]:
                v = vector_add(v, get_v_M_power_x(M_H_powers[1], INF, e(L[c-1], N), x), INF)
                c = R[c-1]
            else:
                c = L[c-1]
        p, logp = 1, 0
        while (p*2)*h < min(h1, h2):
            p, logp = p*2, logp+1
        while p > 1:  # log(p) times => Total Time: O(k cycles * log(p) times * (N^2 * log(delta_h))) = O(N^3 * log(logB)^2 + N^2 * (logB)^2) = O(N^3 * logB) assumed O(N) = O(logB)
            if min(h1, h2) - p*h <= 0:
                p, logp = p//2, logp-1
                continue
            ok1, new_x1 = get_multiple_steps_position(M_H_powers[1], prefix_M_H_powers[h], INF, logp, v, h1-p*h, e(c, N), x1)
            ok2, new_x2 = get_multiple_steps_position(M_H_powers[1], prefix_M_H_powers[h], INF, logp, v, h2-p*h, e(c, N), x2)
            if not ok1 or not ok2:
                p, logp = p//2, logp-1
                continue
            h1, x1 = h1-p*h, new_x1
            h2, x2 = h2-p*h, new_x2
            p, logp = p//2, logp-1
        prev_c = c
    return h1+h2

LEFT, RIGHT = range(2)
for case in xrange(input()):
    print 'Case #%d: %s' % (case+1, infinitree())
