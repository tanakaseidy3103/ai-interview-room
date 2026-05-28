import cv2


def main() -> None:
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Erro: nao foi possivel abrir a camera (index 0).")
        return

    print("Camera aberta. Pressione Q para sair.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Erro ao ler frame da camera.")
            break

        cv2.imshow("AI Interview Room - Camera Preview", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
