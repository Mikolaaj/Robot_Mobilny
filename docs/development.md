# Zasady pracy przy kolejnych fazach

Uzgodnione z użytkownikiem: każdą kolejną fazę rozwijamy na osobnej gałęzi.
Użytkownik chce sam wykonywać kroki: wyjaśniamy cel i komendy przed zmianami,
chyba że bezpośrednio poprosi o implementację lub aktualizację plików.

1. Sprawdź git status. Nie nadpisuj niezapisanych zmian.
2. Nowe zadanie rozpocznij z aktualnego main po scaleniu poprzedniego PR:

```bash
git switch main
git pull --ff-only origin main
git switch -c codex/phase4-description
```

Nazwa powyżej to przykład fazy 4; dobieraj ją do aktualnego zadania.
Nie przenoś niedokończonej fazy na main. Poprawki tej samej fazy kontynuuj
na jej istniejącej gałęzi, obecnie ci-cd-setup.

3. Zmieniaj kod i zgodną z nim dokumentację. Wyjaśnij pliki, przepływ danych,
   budowanie, uruchomienie, wynik, testy, diagnostykę i pojęcia.
4. Uruchom lokalne sprawdzenia odpowiednie do zmian.
5. Commit i push gałęzi. Otwórz PR do main.
6. Sprawdź CI dla najnowszego commita i przejrzyj diff.
7. Scal PR dopiero po zielonym CI i przeglądzie zmian.
8. Zaktualizuj lokalny main przed rozpoczęciem następnej fazy.

CI nie scala PR automatycznie. Sam workflow nie blokuje przycisku Merge;
obowiązkowe kontrole można osobno skonfigurować w regułach gałęzi GitHub.
Nie wysyłamy .venv, build/install/log ani sekretów do repozytorium.
