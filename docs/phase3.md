# Faza 3 — GitHub Actions, CI/CD i Docker

## Stan i zakres

Konfiguracja CI została wysłana na gałąź codex/ci-setup (commit 0afd43d).
Lokalnie zaliczono formatowanie, analizę Ruff, test C++ kinematyki,
6 testów Pythona i integracyjny test ROS. Wynik uruchomienia na GitHubie
musi zostać sprawdzony w Actions; nie potwierdzamy go na podstawie pushu.
Dockerfile, budowanie obrazu oraz publikowanie do GHCR (CD) pozostają do
zrobienia. Cała faza 3 nie jest jeszcze zakończona.

## Co zbudowaliśmy i dlaczego

CI sprawdza kod na osobnej maszynie, aby wychwycić brakujące zależności,
błędy kompilacji, testów i niezgodne formatowanie przed scaleniem zmian.
Nie steruje robotem i nie uruchamia GUI Gazebo.

Przepływ: push/PR → checkout → Ubuntu 24.04 + ROS Jazzy → zależności
→ analiza i formatowanie → budowanie C++ → testy jednostkowe
→ budowanie ROS → test integracyjny → wynik w GitHub Actions.

## Pliki

- .github/workflows/ci.yml: wyzwalacze push, pull_request i workflow_dispatch,
  runner Ubuntu 24.04, timeout 30 minut, uprawnienie contents:read i kroki CI.
  checkout pobiera kod. setup-ros instaluje środowisko ROS. Każdy krok run
  uruchamia osobną powłokę, dlatego setup.bash ładowany jest w krokach ROS.
  colcon test-result zwraca niezerowy kod przy błędach testów, co kończy CI
  niepowodzeniem także wtedy, gdy samo colcon test zakończyło się poprawnie.
- requirements-dev.txt: przypięta wersja Ruff 0.11.13.
- pyproject.toml: Python 3.12, długość linii 100 i reguły Ruff. Obejmuje również
  python_peer i fibonacci_server, które nie mają rozszerzenia .py.
- .clang-format: LLVM, wcięcia 2 spacje, długość linii 100. CI używa wersji 18.
- .gitignore: pomija .venv, build/install/log, cache i lokalne .vscode.

CI to budowanie i weryfikacja. CD to dostarczanie artefaktu, np. publikowanie
obrazu do rejestru GHCR. Obecny workflow realizuje CI; nie publikuje obrazu.

## Lokalne budowanie, uruchamianie i testy

```bash
cd ~/Desktop/Robot_Mobilny
source tools/activate.bash
python -m pip install -r requirements-dev.txt
ruff check examples/phase1 ros2_ws/src/amr_learning
ruff format --check examples/phase1 ros2_ws/src/amr_learning
clang-format-18 --dry-run --Werror examples/phase1/kinematics.hpp examples/phase1/main.cpp examples/phase1/test_kinematics.cpp ros2_ws/src/amr_learning/src/cpp_peer.cpp
cmake -S examples/phase1 -B build/phase1 -G Ninja
cmake --build build/phase1
ctest --test-dir build/phase1 --output-on-failure
python -m unittest discover -s examples/phase1 -v
cd ros2_ws
python -m colcon build --symlink-install --packages-select amr_learning --cmake-args -DPython3_EXECUTABLE=/usr/bin/python3
source install/setup.bash
python -m colcon test --packages-select amr_learning --event-handlers console_direct+
python -m colcon test-result --verbose
```

Oczekiwane: All checks passed, 6 files already formatted, brak komunikatów
clang-format, CTest 100% tests passed, unittest 6 testów OK, ROS 1 test,
0 errors i 0 failures. Więcej plików w przyszłości zmieni liczbę testów/plików.
Workflow uruchamia się po pushu lub otwarciu PR. Ręczne uruchamianie przez
Run workflow jest dostępne po obecności workflow na domyślnej gałęzi.

## GitHub: weryfikacja i diagnostyka

Otwórz https://github.com/Mikolaaj/Robot_Mobilny/actions i wybierz przebieg
CI dla swojej gałęzi i commita. Zielony wynik oznacza zaliczone sprawdzenia;
czerwony wymaga odczytania logu pierwszego nieudanego kroku.
Push zakończony sukcesem nie oznacza automatycznie zaliczonego CI.

Przy błędzie formatu użyj lokalnie ruff format i clang-format -i, obejrzyj
zmiany, powtórz sprawdzenia i wyślij poprawkę. Przy błędzie ROS sprawdź log
build/test oraz source setup.bash. Przy błędzie instalacji sprawdź log apt/pip.
Nie pomijaj nieudanego kroku przez continue-on-error.

Ćwiczenie: znajdź w logu Actions wynik testu communication_integration
oraz sześciu testów Pythona. Porównaj je z wynikami lokalnymi.

## Zakończenie fazy

Pozostaje potwierdzić zielony przebieg CI, dodać i przetestować Dockerfile,
ustalić i uruchomić publikowanie obrazu do GHCR, uzupełnić dokumentację,
a następnie scalić PR po sprawdzeniu najnowszego commita.

Commit dokumentacji:

```bash
git add README.md docs/architecture.md docs/phase3.md docs/development.md
git commit -m "Document phase 3 CI status and branch workflow"
git push
```

Po tym etapie rozumiesz workflow, runner, job, step, wyzwalacze,
kody zakończenia, CI/CD i przegląd zmian przez PR.
