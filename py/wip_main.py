import os
import sys
import random
import json
import time
import urllib.request
import urllib.error
from copy import deepcopy
import collections

# ゲームサーバのアドレス / トークン
GAME_SERVER = os.getenv('GAME_SERVER', 'https://2022contest.gbc.tenka1.klab.jp')
TOKEN = os.getenv('TOKEN', 'e61f03da161605f896fe3d364a1bd251')

TL_MS = 500
N = 5
Dj = [+1, 0, -1, 0]
Dk = [0, +1, 0, -1]
N_AGENT = 6

COLORED = 1
PERFECT_COLOERED = 2

# ゲームサーバのAPIを叩く
def call_api(x: str) -> dict:
    url = f'{GAME_SERVER}{x}'
    # 5xxエラーの際は100ms空けて5回までリトライする
    for i in range(5):
        print(url, flush=True)
        try:
            with urllib.request.urlopen(url) as res:
                return json.loads(res.read())
        except urllib.error.HTTPError as err:
            if 500 <= err.code and err.code < 600:
                print(err.code)
                time.sleep(0.1)
                continue
            else:
                raise
        except ConnectionResetError as err:
            print(err)
            time.sleep(0.1)
            continue
    raise Exception('Api Error')


# game_idを取得する
# 環境変数で指定されていない場合は練習試合のgame_idを返す
def get_game_id() -> int:
    # 環境変数にGAME_IDが設定されている場合これを優先する
    if os.getenv('GAME_ID'):
        return int(os.getenv('GAME_ID'))

    # start APIを呼び出し練習試合のgame_idを取得する
    mode = 0
    delay = 0

    start = call_api(f'/api/start/{TOKEN}/{mode}/{delay}')
    if start['status'] == 'ok' or start['status'] == 'started':
        return start['game_id']

    raise Exception(f'Start Api Error : {start}')


# d方向に移動するように移動APIを呼ぶ
def call_move(game_id: int, d: int) -> dict:
    return call_api(f'/api/move/{TOKEN}/{game_id}/{d}')


# ゲーム状態クラス
class State:
    def __init__(self, field, agent):
        self.field = deepcopy(field)
        self.agent = deepcopy(agent)

    # idxのエージェントがいる位置のfieldを更新する
    def paint(self, idx: int):
        i, j, k, _ = self.agent[idx]
        if self.field[i][j][k][0] == -1:
            # 誰にも塗られていない場合はidxのエージェントで塗る
            self.field[i][j][k][0] = idx
            self.field[i][j][k][1] = 2
        elif self.field[i][j][k][0] == idx:
            # idxのエージェントで塗られている場合は完全に塗られた状態に上書きする
            self.field[i][j][k][1] = 2
        elif self.field[i][j][k][1] == 1:
            # idx以外のエージェントで半分塗られた状態の場合は誰にも塗られていない状態にする
            self.field[i][j][k][0] = -1
            self.field[i][j][k][1] = 0
        else:
            # idx以外のエージェントで完全に塗られた状態の場合は半分塗られた状態にする
            self.field[i][j][k][1] -= 1

    # エージェントidxをd方向に回転させる
    # 方向については問題概要に記載しています
    def rotate_agent(self, idx: int, d: int):
        self.agent[idx][3] += d
        self.agent[idx][3] %= 4

    # idxのエージェントを前進させる
    # マス(i, j, k)については問題概要に記載しています
    def move_forward(self, idx: int):
        i, j, k, d = self.agent[idx]
        jj = j + Dj[d]
        kk = k + Dk[d]
        if jj >= N:
            self.agent[idx][0] = i // 3 * 3 + (i % 3 + 1) % 3  # [1, 2, 0, 4, 5, 3][i]
            self.agent[idx][1] = k
            self.agent[idx][2] = N - 1
            self.agent[idx][3] = 3
        elif jj < 0:
            self.agent[idx][0] = (1 - i // 3) * 3 + (4 - i % 3) % 3  # [4, 3, 5, 1, 0, 2][i]
            self.agent[idx][1] = 0
            self.agent[idx][2] = N - 1 - k
            self.agent[idx][3] = 0
        elif kk >= N:
            self.agent[idx][0] = i // 3 * 3 + (i % 3 + 2) % 3  # [2, 0, 1, 5, 3, 4][i]
            self.agent[idx][1] = N - 1
            self.agent[idx][2] = j
            self.agent[idx][3] = 2
        elif kk < 0:
            self.agent[idx][0] = (1 - i // 3) * 3 + (3 - i % 3) % 3  # [3, 5, 4, 0, 2, 1][i]
            self.agent[idx][1] = N - 1 - j
            self.agent[idx][2] = 0
            self.agent[idx][3] = 1
        else:
            self.agent[idx][1] = jj
            self.agent[idx][2] = kk

    # エージェントが同じマスにいるかを判定する
    def is_same_pos(self, a: [int], b: [int]) -> bool:
        return a[0] == b[0] and a[1] == b[1] and a[2] == b[2]

    # idxのエージェントがいるマスが自分のエージェントで塗られているかを判定する
    def is_owned_cell(self, idx: int) -> bool:
        i = self.agent[idx][0]
        j = self.agent[idx][1]
        k = self.agent[idx][2]
        return self.field[i][j][k][0] == idx

    # 全エージェントの移動方向の配列を受け取り移動させてフィールドを更新する
    # -1の場合は移動させません(0~3は移動APIのドキュメント記載と同じです)
    def move(self, move: [int]):
        # エージェントの移動処理
        for idx in range(6):
            if move[idx] == -1:
                continue
            self.rotate_agent(idx, move[idx])
            self.move_forward(idx)

        # フィールドの更新処理
        for idx in range(6):
            if move[idx] == -1:
                continue
            ok = True
            for j in range(6):
                if idx == j or move[j] == -1 or not self.is_same_pos(self.agent[idx], self.agent[j]) or self.is_owned_cell(idx):
                    continue
                # 移動した先にidx以外のエージェントがいる場合は修復しか行えないのでidxのエージェントのマスではない場合は更新しないようにフラグをfalseにする
                ok = False
                break

            if not ok:
                continue
            self.paint(idx)

ME = 0

def get_rank(colored):
    ranks = sorted([(colored[i],i) for i in range(N_AGENT)], reverse=True)
    return ranks.index(((colored[ME],ME))), ranks
class Bot:
    def solve(self):
        game_id = get_game_id()
        history = collections.deque()
        next_d = random.randint(0, 3)
        while True:
            # 移動APIを呼ぶ
            move = call_move(game_id, next_d)
            print('status = {}'.format(move['status']), file=sys.stderr, flush=True)
            if move['status'] == "already_moved":
                continue
            elif move['status'] != 'ok':
                break
            print('turn = {}'.format(move['turn']), file=sys.stderr, flush=True)
            print('score = {} {} {} {} {} {}'.format(move['score'][0], move['score'][1], move['score'][2], move['score'][3], move['score'][4], move['score'][5]), file=sys.stderr, flush=True)


            history.append(next_d)
            if len(history) > 6:
                history.popleft()

            # 4方向で移動した場合を全部シミュレーションする
            best_result = (-N_AGENT, -1, -1, -N*N*6, -N*N*6, -N*N*6, -N*N*6, -N*N*6)
            best_d = []
            for d in range(4):
                m = State(move['field'], move['agent'])
                # 他のエージェントの動きは決め打ち
                m.move([d, 0,0,0,0,0])
                # 自身のエージェントで塗られているマス数をカウントする
                colored = [0] * N_AGENT
                perfect_coloerd = [0] * N_AGENT
                for i in range(6):
                    for j in range(N):
                        for k in range(N):
                            if m.field[i][j][k][0] == -1:
                                # 塗られていないマス
                                continue
                            else:
                                [player, state] = m.field[i][j][k]
                                assert 0<= player < 6, f"player: {player}"
                                colored[player] += 1
                                if state == PERFECT_COLOERED:
                                    perfect_coloerd[player] += 1
                my_rank, ranks = get_rank(colored)
                if my_rank == 0:
                    result = (-my_rank, colored[ME],perfect_coloerd[ME], -ranks[my_rank+1][0], -max(colored[ME+1:]), -sum(colored[ME+1:]),  -sum(perfect_coloerd[ME+1:]))
                else:
                    result = (-my_rank, colored[ME],perfect_coloerd[ME], -ranks[my_rank-1][0], -max(colored[ME+1:]), -sum(colored[ME+1:]),  -sum(perfect_coloerd[ME+1:]))

                if result > best_result:
                    best_result = result
                    best_d = [d]
                elif result == best_result:
                    best_d.append(d)
            if len(history) >= 4 and best_d[0] == history[1] == history[3] and history[0] == history[2]:
                next_d = random.randint(0, 3)
            else:
                next_d = best_d[0]


if __name__ == "__main__":
    bot = Bot()
    bot.solve()
