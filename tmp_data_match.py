#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from decimal import Decimal, ROUND_HALF_UP
import random
import copy
import matplotlib.pyplot as plt

"""
Created on Sat Nov 24 16:42:54 2018

@author: hosokawaai
"""

# 初期変数
DAYS = 30
# 一日あたりの最低選考リスト人数
DAILY_MIN_MEN_NUM = 2
DAILY_MIN_WOMEN_NUM = 2
# 一日あたりの最高選考リスト人数
DAILY_MAX_MEN_NUM = 5
DAILY_MAX_WOMEN_NUM = 5
random.seed(0)
#1日あたりの人数を設定　random.random() * DAILY_MAX_MEN_NUM * DAYS=0.0~1.0*5*30人/30日
MEN_NUM = int(Decimal(random.random() * DAILY_MAX_MEN_NUM * DAYS).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
WOMEN_NUM = int(Decimal(random.random() * DAILY_MAX_WOMEN_NUM * DAYS).quantize(Decimal('0'), rounding=ROUND_HALF_UP))
#0.3 * 5 * 2 = 3人/2日　※1.5人/日　< 一日当たり最小値 * 日数　＝　4人/2日なので、4人/2日を適用
if MEN_NUM // DAYS < DAILY_MIN_MEN_NUM:
    MEN_NUM = DAILY_MIN_MEN_NUM * DAYS
if WOMEN_NUM // DAYS < DAILY_MIN_WOMEN_NUM:
    WOMEN_NUM = DAILY_MIN_WOMEN_NUM * DAYS


# G-Sアルゴリズム
def gale_shapley(a, b):
    single_as = sorted({key for key in a.keys()}, reverse=True)  # single_asにaの要素を数値の大きい順に並べる
    single_bs = sorted({key for key in b.keys()}, reverse=True)  # single_bsにbの要素を数値の大きい順に並べる
    engaged = {}  # engagedの箱を作る
    for single_a in single_as:  # single_asの0番目から順にsingle_aに入れる by obo2
        for single_b in single_bs:  # single_bsの0番目から順にsingle_bに入れる by obo2
            engaged[single_a, single_b] = False  # single_aとsingle_bのペア= Falseを作る by obo2

    while len(single_as) != 0:  # single_asの要素がなくなるまで続ける by obo2
        single_a = single_as.pop()  # single_asの末から取り出した要素をsingle_aに入れる by obo2

        for target_b in a[single_a]:  # aの好みの人を順にtarget_bに入れる by obo2
            if target_b in b:  #
                if single_a in b[target_b]:  # もしsingle_aがbに好む人が含まれていたら'test 0'を返す by obo2
                    # 相手target_bの選好リストにsingle_aが存在
                    if target_b in single_bs:  # もしtarget_bが独身集合single_bsにあったら、engaged = True by obo2
                        engaged[single_a, target_b] = True
                        single_bs.remove(target_b)  # target_bをsingle_bsから外す by obo2
                        break
                    else:
                        # すでに婚約者がいる場合、好みの順序を評価
                        # target_bの婚約相手を取得する
                        engaged_a = [k for k, v in engaged.items() if v is True and target_b in k][0][0]
                        target_a_list = b[target_b]  # bのaに対する順序をtarget_a_listに入れる by obo2
                        # 婚約者とsingle_aの順位を比較
                        if target_a_list.index(single_a) < target_a_list.index(
                                engaged_a):  # aもし、すでにペアになっている人の順番が高いと? by obo2
                            # 好みの優先順位を調べて今回のほうが好まれていたら元の婚約者との婚約を破棄
                            engaged[engaged_a, target_b] = False  # ペアは解消
                            single_as.append(engaged_a)  # ペア解消となったengaged_aはsingle_asに加わる by obo2
                            # 改めて婚約
                            engaged[single_a, target_b] = True  # single_a, target_bがペアになる by obo2
                            break
    return [k for k, v in engaged.items() if v is True]


def improve_gale_shapley(s, l_men, l_women):
    m_list = []
    v = copy.deepcopy(l_men)
    v.update(l_women)
    l_list = []
    l_item = copy.deepcopy(v)
    for key in v.keys():
        if key in [item for sublist in s for item in sublist]:
            del l_item[key]
    l_list.append(l_item)
    r_list = []
    r_item = create_r(v, l_list[0])
    r_list.append(r_item)
    i = 1
    while True:
        m = gale_shapley(l_list[i - 1], r_list[i - 1])
        m_list.append(m)  # (L,R)のマッチング結果
        if r_perfect_check(r_list[i - 1], m) is False:  # R-perfectでなければFalse
            ab = set_ab(i - 1, r_list[i - 1], m)  # Rの男性をセットする
            l_list[i - 1].update(ab)  # L_listとABの男性の要素を足す
            r_list[i - 1] = create_r(v, l_list[i - 1])  # R = V-L
            m = gale_shapley(l_list[i - 1], r_list[i - 1])  # (L,R)上でG-Sアルゴリズムの実装
            m_list.append(m)
            if not r_perfect_check(r_list[i - 1], m):
                ab = set_ab(i, r_list[i - 1], m)
                l_list.append({})
                l_list[i].update(l_list[i - 1])
                l_list[i].update(ab)
                r_item = create_r(v, l_list[i])
                r_list.append(r_item)
                i = i + 1
            else:
                break
        else:
            break
    return m_list


def r_perfect_check(r, m):
    for d_key in r.keys():
        if d_key not in [m_key for sublist in m for m_key in sublist]:
            return False
    return True


def create_r(v, l):
    r = copy.deepcopy(v)
    for key in l.keys():
        del r[key]
    return r


def set_ab(i, r_list, m):
    sex = 'M'
    if i % 2 == 0:
        sex = 'W'
    ab = copy.deepcopy(r_list)
    for r_key in r_list.keys():
        if sex in r_key:
            del ab[r_key]
    for m_key in [item for sublist in m for item in sublist]:
        if m_key in ab:
            del ab[m_key]

    return ab


# 選好リスト作成
def create_priority(n, m):
    men_list = []
    women_list = []
    # Mi,Wiの辞書キーを生成
    for men in range(n):
        men_list.append('M' + str(men))
    for women in range(m):
        women_list.append(('W' + str(women)))

    # Wiの選好リストに入っていないMiは、Wiを選好リストに含めない
    # Wiの選好リストを先に作成
    women_dict = {}
    preference_rate = 0.07  # 選好に含める確率を定める

    for key in women_list:
        tmp_list = []
        # 選好順位をランダムに設定
        random.shuffle(men_list)
        tmp_list.extend(list(men_list))
        # **選好判定**
        remove_list = []
        for tmp in tmp_list:
            if len(tmp_list) - 1 == len(remove_list):  # 少なくとも一人は選好リストに含める
                pass
            elif random.random() >= preference_rate:
                remove_list.append(tmp)
        for remove in remove_list:
            tmp_list.remove(remove)
        tmp_list = tmp_list[:10]  # womenの選好リストに含む数は最大10人までとする
        women_dict[key] = tmp_list

    # Wiの選好リストに入っていないMiは、Wiを選好リストに含めない
    # →Wiの選好リストに含まれているかを確認し、元となるMiの選好リストを作成
    men_dict = {}
    for key in men_list:
        men_dict[key] = []
        for k, v in women_dict.items():
            if key in v:
                men_dict[key].append(k)

    for k, v in men_dict.items():
        tmp_list = v
        # MiはWiすべてを順序付ける必要はない。
        # →選好に含める確率を元に選好リストから除外処理実行
        remove_list = []
        for tmp in tmp_list:
            if len(tmp_list) - 1 == len(remove_list):  # 少なくとも一人は選好リストに含める
                pass
            elif random.random() >= preference_rate:
                remove_list.append(tmp)
        for remove in remove_list:
            tmp_list.remove(remove)

        men_dict[k] = tmp_list
    return men_dict, women_dict


# 不満足度計算
def calc_dissatisfaction(married, men_dict, women_dict):
    dissatisfaction_score = 0
    total_dict = copy.deepcopy(men_dict)
    total_dict.update(women_dict)
    for m in married:
        tmp_value = total_dict[m[0]]
        dissatisfaction_score += tmp_value.index(m[1])
        tmp_value = total_dict[m[1]]
        dissatisfaction_score += tmp_value.index(m[0])
        del total_dict[m[0]], total_dict[m[1]]
    for k, v in total_dict.items():
        dissatisfaction_score += len(v)
    return dissatisfaction_score


def daily_exec(l_men, l_women, days, improve_flg):
    orig_l_key = list(l_men.keys()) + list(l_women.keys())
    orig_l_men = copy.deepcopy(l_men)
    orig_l_women = copy.deepcopy(l_women)
    unmatched_l_men = copy.deepcopy(l_men)
    unmatched_l_women = copy.deepcopy(l_women)
    daily_dissatisfaction = 0
    total_m_list = []
    for day in range(days):
        daily_l_men = {}
        daily_l_women = {}
        # 残った人達を残日数で割る
        daily_men_num = len(unmatched_l_men) // (days - day)
        daily_women_num = len(unmatched_l_women) // (days - day)
        # 一日分の人をランダム抽出
        for i in range(daily_men_num):
            key, val = random.choice(list(unmatched_l_men.items()))
            daily_l_men.update({key: val})
            del unmatched_l_men[key]
        daily_l_men = dict(sorted(daily_l_men.items()))

        for i in range(daily_women_num):
            key, val = random.choice(list(unmatched_l_women.items()))
            daily_l_women.update({key: val})
            del unmatched_l_women[key]
        daily_l_women = dict(sorted(daily_l_women.items()))

        # Wiの選好リストに入っていないMiの選好リストを除外
        for key, value in daily_l_men.items():
            for v in value:
                if v not in daily_l_women:
                    daily_l_men[key].remove(v)
                elif key not in daily_l_women[v]:
                    daily_l_men[key].remove(v)
        s = gale_shapley(daily_l_men, daily_l_women)
        if improve_flg:
            m_list = improve_gale_shapley(s, daily_l_men, daily_l_women)
            total_m_list.extend(m_list[-1])
            daily_dissatisfaction += calc_dissatisfaction(m_list[-1], daily_l_men, daily_l_women)
        else:
            total_m_list.extend(s)
            daily_dissatisfaction += calc_dissatisfaction(s, daily_l_men, daily_l_women)
        # マッチングした人たち
        m_keys = [flatten for inner in total_m_list for flatten in inner]
        # マッチングしなかった人たち
        unmatched_keys = list(set(orig_l_key) - set(m_keys))
        for unmatched_key in unmatched_keys:
            if 'M' in unmatched_key:
                unmatched_l_men.update({unmatched_key: l_men[unmatched_key]})
            if 'W' in unmatched_key:
                unmatched_l_women.update({unmatched_key: l_women[unmatched_key]})
    l_men.update(orig_l_men)
    l_women.update(orig_l_women)
    return total_m_list, daily_dissatisfaction


def main():
    for i in range(10):
        random.seed(i)
        l_men, l_women = create_priority(MEN_NUM, WOMEN_NUM)  # 選好リスト作成
        plot_list = []
        xtics = []
        x_range = 0
        for day in range(DAYS):
            if DAYS % (day + 1) == 0:
                s, apparent_s_dissatisfaction = daily_exec(l_men, l_women, day+1, False)
                m, apparent_m_dissatisfaction = daily_exec(l_men, l_women, day+1, True)
                print('MEN_PRIORITY:', len(l_men))#男性の数
                print('MEN_PRIORITY:', l_men)#男性の女性に対する選好リスト
                print('WOMEN_PRIORITY:', len(l_women))#女性の数
                print('WOMEN_PRIORITY:', l_women)
                print("**********************************")
                print(str(int(DAYS / (day + 1))) + "日ごと")
                print("Gale-Shapley：S")
                print("■ペア")
                print(s)
                print("■ペア数")
                print(len(s))
                print("■不満足度")
                dissatisfaction_score = calc_dissatisfaction(s, l_men, l_women)
                print("見かけ", apparent_s_dissatisfaction)
                print("実際", dissatisfaction_score)
                print("")
                print("改良版Gale-Shapley：M")
                print("■ペア")
                print(m)
                print("■ペア数")
                print(len(m))
                plot_list.append(len(m))
                xtics.append(str(int(DAYS / (day + 1))))
                print("■不満足度")
                dissatisfaction_score = calc_dissatisfaction(m, l_men, l_women)
                print("見かけ", apparent_m_dissatisfaction)
                print("実際", dissatisfaction_score)
                x_range += 1
        plt.plot(plot_list, label='seed_' + str(i))
        plt.xticks(range(x_range), xtics)
    plt.grid()
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
