# 8번의 업그레이드까지 구현된 코드
# 제한 시간 내 최대한 많은 단어를 맞추는 것으로 변경
# 난이도 설정 가능

import random
import time
import csv
import os
import math
from datetime import datetime
from pygame import mixer

mixer.init()

words = []  # 단어들 저장용
sounds = {}  # 효과음 저장용

RECORD_FILE = "word_game_record.csv"

# 난이도별 설정: (단어 최소 길이, 단어 최대 길이, 제한 시간)
LEVELS = {
    "1": ("쉬움", 2, 4, 60),  # 1글자짜리는 문제로 내기엔 너무 시시해서 제외
    "2": ("보통", 5, 7, 60),
    "3": ("어려움", 8, 99, 50),
}

# 단어 데이터가 저장되어 있는 파일을 로딩하여 단어들을 리스트 객체 변수로 저장
def wordLoad():
    global words
    with open("data/word.txt", "r", encoding="utf-8") as f:
        for line in f:
            words.append(line.strip())

# 효과음을 미리 메모리에 올려둠 (제한 시간 모드에서는 매번 파일을 읽으면 느려짐)
def soundLoad():
    global sounds
    sounds["good"] = mixer.Sound("assets/good.wav")
    sounds["bad"] = mixer.Sound("assets/bad.wav")

# 난이도를 입력받아 (이름, 해당 난이도의 단어 목록, 제한 시간)을 돌려줌
def levelSelect():
    print("=" * 40)
    print("난이도를 선택하세요")
    for key, (name, low, high, limit) in LEVELS.items():
        length = f"{low}~{high}글자" if high < 99 else f"{low}글자 이상"
        print(f"  {key}. {name} ({length}, 제한 시간 {limit}초)")
    print("=" * 40)

    while True:
        choice = input("번호 입력: ").strip()
        if choice in LEVELS:
            name, low, high, limit = LEVELS[choice]
            pool = [w for w in words if low <= len(w) <= high]
            return name, pool, limit
        print("1, 2, 3 중에서 골라주세요.")

def gameRun(level, pool, limit):
    correct = 0
    wrong = 0
    combo = 0  # 현재 연속 정답 수
    max_combo = 0  # 이번 판의 최고 콤보
    score = 0
    quit_early = False  # 중간에 그만뒀는지 여부

    best = bestScore(level)
    print()
    print(f"[{level}] 난이도로 시작합니다. 제한 시간 {limit}초!")
    print(f"역대 최고 점수: {best}점" if best else "아직 기록이 없습니다. 첫 기록에 도전!")
    print("중간에 그만두려면 !q 를 입력하세요.")
    input("준비되면 엔터를 누르세요...")
    print()

    start_time = time.time()

    # 제한 시간이 끝날 때까지 계속 새로운 단어를 제시
    while True:
        remain = limit - (time.time() - start_time)
        if remain <= 0:
            break

        # 해당 난이도의 단어 중에서 임의 단어를 뽑아서 화면에 제시
        target = random.choice(pool)
        print(f"남은 시간 {math.ceil(remain)}초 | 점수 {score} | 콤보 {combo}")
        print("Question:", target)
        answer = input("Answer:").strip()

        if answer == "!q":
            quit_early = True
            break

        if answer == target:
            combo += 1
            max_combo = max(max_combo, combo)
            # 기본 10점 + 콤보 보너스 (콤보 1당 2점, 최대 10점까지)
            bonus = min((combo - 1) * 2, 10)
            score += 10 + bonus
            correct += 1
            print(f"정답! +{10 + bonus}점" + (f" ({combo}콤보!)" if combo >= 2 else ""))
            sounds["good"].play()
        else:
            if combo >= 2:
                print(f"오답 (정답: {target}) - {combo}콤보가 끊겼습니다")
            else:
                print(f"오답 (정답: {target})")
            combo = 0
            wrong += 1
            sounds["bad"].play()
        print()

    elapsed = time.time() - start_time
    scorePrint(level, limit, elapsed, correct, wrong, max_combo, score, best, quit_early)

def scorePrint(level, limit, elapsed, correct, wrong, max_combo, score, best, quit_early):
    total = correct + wrong
    accuracy = (correct / total * 100) if total else 0.0

    print("=" * 40)
    print(f"{'게임 중단' if quit_early else '시간 종료'}! [{level}] 난이도 결과")
    print("=" * 40)
    print(f"맞춘 개수: {correct} / {total}")
    print(f"정확도: {accuracy:.1f}%")
    print(f"최고 콤보: {max_combo}")
    print(f"최종 점수: {score}점")
    print(f"플레이 시간: {elapsed:.2f}초 (제한 {limit}초)")

    # 역대 최고 점수와 비교
    if score > best:
        print(f"신기록 달성! (이전 최고 {best}점)" if best else "첫 기록을 세웠습니다!")
    elif best:
        print(f"역대 최고 점수는 {best}점입니다. 조금만 더!")

    print("결과: 합격 ^_^" if accuracy >= 60 and correct >= 5 else "결과: 불합격 ㅠ_ㅠ")

    recordSave(level, limit, correct, wrong, accuracy, max_combo, score)

# 기록 파일에서 해당 난이도의 역대 최고 점수를 읽어옴 (없으면 0)
def bestScore(level):
    if not os.path.exists(RECORD_FILE):
        return 0

    best = 0
    with open(RECORD_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("난이도") == level:
                try:
                    best = max(best, int(row["점수"]))
                except (ValueError, KeyError, TypeError):
                    continue  # 손상된 줄은 건너뜀
    return best

# 게임 결과를 파일에 누적 저장
def recordSave(level, limit, correct, wrong, accuracy, max_combo, score):
    is_new = not os.path.exists(RECORD_FILE)
    with open(RECORD_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:  # 파일을 처음 만들 때만 제목 줄을 적음
            writer.writerow(["날짜", "난이도", "제한시간", "정답", "오답", "정확도", "최고콤보", "점수"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            level, limit, correct, wrong, f"{accuracy:.1f}", max_combo, score,
        ])

if __name__ == "__main__":
    wordLoad()
    soundLoad()

    # 여러 판을 이어서 할 수 있도록 반복
    try:
        while True:
            level, pool, limit = levelSelect()
            gameRun(level, pool, limit)
            again = input("\n한 판 더 하시겠습니까? (y/n): ").strip().lower()
            if again != "y":
                print("수고하셨습니다!")
                break
    except (KeyboardInterrupt, EOFError):  # Ctrl+C, Ctrl+D로 끝냈을 때
        print("\n게임을 종료합니다.")