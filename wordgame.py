import random
import time
from pygame import mixer

mixer.init()

words = []  # 단어들 저장용

# 단어 데이터가 저장되어 있는 파일을 로딩하여 단어들을 리스트 객체 변수로 저장
def wordLoad():
    global words
    with open("data/word.txt", "r", encoding="utf-8") as f:
        for line in f:
            words.append(line.strip())

def gameRun():
    correct = 0
    start_time = time.time()

    # 단어 입력 횟수는 총 5번을 반복
    for i in range(5):
        # words 리스트에서 임의 단어를 뽑아서 화면에 제시
        target = random.choice(words)
        print("Question:", target)
        answer = input("Answer:").strip()

        if answer == target:
            print("정답!")
            mixer.music.load("assets/good.wav")
            mixer.music.play()
            correct += 1  # 맞춘 개수 카운트
        else:
            print("오답")
            mixer.music.load("assets/bad.wav")
            mixer.music.play()

    elapsed = time.time() - start_time
    scorePrint(correct, elapsed)

def scorePrint(correct, elapsed):
    # 3개 이상 맞추면 합격 출력, 2개 이하로 맞추면 불합격
    print("결과: 합격 ^_^" if correct >= 3 else "결과: 불합격 ㅠ_ㅠ")

    # 게임 시작부터 종료까지 총 걸린 시간 및 맞춘 갯수 출력
    print(f"맞춘 개수: {correct} / 5")
    print(f"걸린 시간: {elapsed:.2f}초")

if __name__ == "__main__":
    wordLoad()
    gameRun()