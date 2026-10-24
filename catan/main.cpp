#include <array>
#include <bitset>
#include <cstdint>
#include <iostream>
#include <random>
#include <sys/types.h>
#include "types.cpp"

using std::uniform_int_distribution;

#include <cstdint>

uint8_t rollDice(){
  return std::uniform_int_distribution<uint8_t>(1, 6)(rng) +
         uniform_int_distribution<uint8_t>(1, 6)(rng);
}

void produce_resources(uint8_t diceRoll) {
    uint32_t tiles = GAMESTATE.tile_numbers[diceRoll];
    while (tiles) {
        int tile = std::__countr_zero(tiles);
        tiles &= tiles - 1;
        if (tile == THIEF_TILE) continue;
        RESOURCE_TYPE resource = GAMESTATE.tile_resources[tile - 1];
        const uint8_t settlement_spots = tile_settlements[tile - 1];
        for (int i = 0; i < N_PLAYERS; i++) {
            if ((GAMESTATE.settlements[i] & settlement_spots) > 0) {
                GAMESTATE.player_resources[i][resource] += std::__popcount(GAMESTATE.settlements[i] & settlement_spots) +
                    std::__popcount(GAMESTATE.cities[i] & settlement_spots);
            }
        }
    }
}

void move_thief(uint8_t dest_tile, PLAYER_COLOR player, PLAYER_COLOR player_to_rob) {
    THIEF_TILE = dest_tile;
    uint8_t robbed_resource = GAMESTATE.player_resources[player_to_rob][std::uniform_int_distribution<uint8_t>(1, 5)(rng)];
    GAMESTATE.player_resources[player_to_rob][robbed_resource]--;
    GAMESTATE.player_resources[player][robbed_resource]++;
}

void buy_dev_card(PLAYER_COLOR player) {
    if (GAMESTATE.deck_pointer == N_DEV_CARDS_TOTAL) return;
    if (!buy(player, DEV_CARD)) return;
    DEV_CARD_TYPE card = GAMESTATE.deck_dev_cards[GAMESTATE.deck_pointer];
    GAMESTATE.player_dev_cards[player][card]++;
    if (card == VP) {
        GAMESTATE.victory_points[player]++;
    }
}

void buy_city(PLAYER_COLOR player, uint64_t spot) {
    if (std::__popcount(GAMESTATE.cities[player]) == 4 || std::__popcount(GAMESTATE.settlements[player]) == 0 || (GAMESTATE.settlements[player] & spot) == 0) return;
    if (!buy(player, CITY)) return;
    GAMESTATE.cities[player] |= spot;
    GAMESTATE.victory_points[player]++;
}

void buy_settlement(PLAYER_COLOR player, uint64_t spot) {
    buy(player, SETTLEMENT);
    GAMESTATE.settlements[player] |= spot;
    GAMESTATE.victory_points[player]++;
}

int longest_from(
    uint8_t vertex,
    const std::bitset<N_ROADS>& owned,
    uint64_t blocked,
    std::bitset<N_ROADS>& used
) {
    if (blocked & (1ULL << (vertex - 1)))
        return 0;

    int best = 0;

    for (int road = 0; road < 72; road++) {
        if (!settlement_roads[vertex - 1].test(road) ||
            !owned.test(road) ||
            used.test(road))
            continue;

        used.set(road);

        const uint8_t* settlements = road_to_settlements[road];
        uint8_t next = (settlements[0] == vertex) ? settlements[1] : settlements[0];

        best = std::max(
            best,
            1 + longest_from(next, owned, blocked, used)
        );

        used.reset(road);
    }

    return best;
}

int count_longest_road(uint8_t player) {
    const std::bitset<N_ROADS>& owned = GAMESTATE.roads[player];

    // Find all opponent settlements and cities
    uint64_t blocked = 0;

    for (int i = 0; i < 4; i++) {
        if (i == player)
            continue;

        blocked |= GAMESTATE.settlements[i];
        blocked |= GAMESTATE.cities[i];
    }

    int best = 0;
    std::bitset<N_ROADS> used{};

    for (int road = 0; road < 72; road++) {
        if (!owned.test(road))
            continue;

        used.set(road);

        const uint8_t* settlements = road_to_settlements[road];

        best = std::max({
            best,
            1 + longest_from(settlements[0], owned, blocked, used),
            1 + longest_from(settlements[1], owned, blocked, used)
        });

        used.reset(road);
    }

    return best;
}

void buy_road(PLAYER_COLOR player, int spot) {
    buy(player, ROAD_BUILD);
    GAMESTATE.roads[player].set(spot);
    count_longest_road(player);
}

void play_knight_card(PLAYER_COLOR player, uint8_t dest_tile, PLAYER_COLOR player_to_rob) {
    move_thief(dest_tile, player, player_to_rob);
    GAMESTATE.knight_cards[player]++;
    if (GAMESTATE.knight_cards[player] > GAMESTATE.biggest_army) {
        GAMESTATE.biggest_army = GAMESTATE.knight_cards[player];
        GAMESTATE.victory_points[player] += 2;
        if (GAMESTATE.biggest_army > 5) {
            GAMESTATE.victory_points[GAMESTATE.biggest_army] -= 2;
        }
        GAMESTATE.biggest_army_holder = player;
    }
}

int main(int argc, char* argv[]) {
    // TODO: Parse command-line arguments when needed.
    (void)argc;
    (void)argv;

    std::cout << "Welcome to Catan!\n";

    // TODO: Initialize the game and run the main loop.

    return 0;
}
