import random

import pygame


ZELLGROESSE = 25

GROESSEN = [(640, 400), (800, 500), (1000, 625)]
GESCHWINDIGKEITEN = [("Langsam", 180), ("Normal", 110), ("Schnell", 65)]
SYMBOL_ANZAHLEN = [1, 2, 3]

HINTERGRUND = (18, 24, 32)
GITTER = (30, 40, 52)
SCHLANGE = (76, 201, 120)
KOPF = (126, 231, 135)
SYMBOL = (255, 105, 97)
TEXT = (235, 241, 245)


def neue_runde(breite, hoehe, symbol_anzahl):
    schlange = [(breite // (2 * ZELLGROESSE), hoehe // (2 * ZELLGROESSE))]
    richtung = (1, 0)
    symbole = neue_symbole(schlange, breite, hoehe, symbol_anzahl)
    return schlange, richtung, symbole, 0, False


def neue_symbole(schlange, breite, hoehe, anzahl):
    freie_felder = [
        (x, y)
        for x in range(breite // ZELLGROESSE)
        for y in range(hoehe // ZELLGROESSE)
        if (x, y) not in schlange
    ]
    return random.sample(freie_felder, min(anzahl, len(freie_felder)))


def verarbeite_ereignisse(richtung, spiel_beendet):
    neue_richtung = richtung
    neustart = False
    for ereignis in pygame.event.get():
        if ereignis.type == pygame.QUIT:
            return neue_richtung, spiel_beendet, neustart, False
        if ereignis.type != pygame.KEYDOWN:
            continue
        if spiel_beendet and ereignis.key == pygame.K_r:
            neustart = True
            continue
        richtungen = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_a: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_d: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_w: (0, -1),
            pygame.K_DOWN: (0, 1),
            pygame.K_s: (0, 1),
        }
        moegliche_richtung = richtungen.get(ereignis.key)
        if moegliche_richtung and moegliche_richtung != (-richtung[0], -richtung[1]):
            neue_richtung = moegliche_richtung
    return neue_richtung, spiel_beendet, neustart, True


def bewege_schlange(schlange, richtung, symbole, breite, hoehe):
    kopf_x, kopf_y = schlange[0]
    neue_position = (kopf_x + richtung[0], kopf_y + richtung[1])
    spielfeld_breite = breite // ZELLGROESSE
    spielfeld_hoehe = hoehe // ZELLGROESSE

    if (
        not 0 <= neue_position[0] < spielfeld_breite
        or not 0 <= neue_position[1] < spielfeld_hoehe
        or neue_position in schlange
    ):
        return False, symbole, False

    schlange.insert(0, neue_position)
    if neue_position in symbole:
        symbole.remove(neue_position)
        return True, symbole, True
    schlange.pop()
    return True, symbole, False


def zeichne(fenster, schlange, symbole, punkte, schrift, spiel_beendet, breite, hoehe):
    fenster.fill(HINTERGRUND)
    for x in range(0, breite, ZELLGROESSE):
        pygame.draw.line(fenster, GITTER, (x, 0), (x, hoehe))
    for y in range(0, hoehe, ZELLGROESSE):
        pygame.draw.line(fenster, GITTER, (0, y), (breite, y))

    for symbol in symbole:
        symbol_mitte = (
            symbol[0] * ZELLGROESSE + ZELLGROESSE // 2,
            symbol[1] * ZELLGROESSE + ZELLGROESSE // 2,
        )
        pygame.draw.circle(fenster, SYMBOL, symbol_mitte, ZELLGROESSE // 2 - 3)

    for index, (x, y) in enumerate(schlange):
        farbe = KOPF if index == 0 else SCHLANGE
        rechteck = pygame.Rect(
            x * ZELLGROESSE + 2,
            y * ZELLGROESSE + 2,
            ZELLGROESSE - 4,
            ZELLGROESSE - 4,
        )
        pygame.draw.rect(fenster, farbe, rechteck, border_radius=5)

    punkte_text = schrift.render(f"Punkte: {punkte}", True, TEXT)
    fenster.blit(punkte_text, (12, 10))

    if spiel_beendet:
        meldung = schrift.render("Game Over - R zum Neustart", True, TEXT)
        position = meldung.get_rect(center=(breite // 2, hoehe // 2))
        pygame.draw.rect(fenster, HINTERGRUND, position.inflate(24, 18), border_radius=6)
        fenster.blit(meldung, position)


def menue(fenster, schrift):
    auswahl = [0, 1, 0]
    markierung = 0
    uhr = pygame.time.Clock()
    labels = ["Bildschirmgroesse", "Geschwindigkeit", "Sammelpunkte gleichzeitig"]

    while True:
        for ereignis in pygame.event.get():
            if ereignis.type == pygame.QUIT:
                return None
            if ereignis.type != pygame.KEYDOWN:
                continue
            if ereignis.key in (pygame.K_UP, pygame.K_w):
                markierung = (markierung - 1) % len(labels)
            elif ereignis.key in (pygame.K_DOWN, pygame.K_s):
                markierung = (markierung + 1) % len(labels)
            elif ereignis.key in (pygame.K_LEFT, pygame.K_a):
                auswahl[markierung] = (auswahl[markierung] - 1) % 3
            elif ereignis.key in (pygame.K_RIGHT, pygame.K_d):
                auswahl[markierung] = (auswahl[markierung] + 1) % 3
            elif ereignis.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                breite, hoehe = GROESSEN[auswahl[0]]
                _, bewegungsintervall = GESCHWINDIGKEITEN[auswahl[1]]
                return breite, hoehe, bewegungsintervall, SYMBOL_ANZAHLEN[auswahl[2]]

        fenster.fill(HINTERGRUND)
        titel = schrift.render("SNAKE - Einstellungen", True, KOPF)
        fenster.blit(titel, titel.get_rect(center=(fenster.get_width() // 2, 70)))
        hinweis = schrift.render("Wahlen mit Pfeilen/A-D, Start mit Enter", True, TEXT)
        fenster.blit(hinweis, hinweis.get_rect(center=(fenster.get_width() // 2, 115)))

        werte = [
            [f"{breite} x {hoehe}" for breite, hoehe in GROESSEN],
            [name for name, _ in GESCHWINDIGKEITEN],
            [str(anzahl) for anzahl in SYMBOL_ANZAHLEN],
        ]
        for index, label in enumerate(labels):
            farbe = KOPF if index == markierung else TEXT
            text = f"> {label}: {werte[index][auswahl[index]]}" if index == markierung else f"  {label}: {werte[index][auswahl[index]]}"
            zeile = schrift.render(text, True, farbe)
            fenster.blit(zeile, (100, 190 + index * 60))

        pygame.display.flip()
        uhr.tick(30)


def main():
    pygame.init()
    fenster = pygame.display.set_mode(GROESSEN[1])
    pygame.display.set_caption("Snake")
    einstellungen = menue(fenster, pygame.font.Font(None, 32))
    if einstellungen is None:
        pygame.quit()
        return
    breite, hoehe, bewegungsintervall, symbol_anzahl = einstellungen
    fenster = pygame.display.set_mode((breite, hoehe))
    uhr = pygame.time.Clock()
    schrift = pygame.font.Font(None, 32)
    schlange, richtung, symbole, punkte, spiel_beendet = neue_runde(
        breite, hoehe, symbol_anzahl
    )
    zeit_seit_bewegung = 0
    aktiv = True

    while aktiv:
        vergangene_zeit = uhr.tick(60)
        richtung, spiel_beendet, neustart, aktiv = verarbeite_ereignisse(
            richtung, spiel_beendet
        )
        if not aktiv:
            break
        if spiel_beendet and neustart:
            schlange, richtung, symbole, punkte, spiel_beendet = neue_runde(
                breite, hoehe, symbol_anzahl
            )
            zeit_seit_bewegung = 0
        elif not spiel_beendet:
            zeit_seit_bewegung += vergangene_zeit
            if zeit_seit_bewegung >= bewegungsintervall:
                zeit_seit_bewegung = 0
                erfolgreich, symbole, gefressen = bewege_schlange(
                    schlange, richtung, symbole, breite, hoehe
                )
                if erfolgreich and gefressen:
                    punkte += 1
                    fehlende_symbole = symbol_anzahl - len(symbole)
                    if fehlende_symbole > 0:
                        symbole.extend(
                            neue_symbole(schlange + symbole, breite, hoehe, fehlende_symbole)
                        )
                elif not erfolgreich:
                    spiel_beendet = True

        zeichne(fenster, schlange, symbole, punkte, schrift, spiel_beendet, breite, hoehe)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
