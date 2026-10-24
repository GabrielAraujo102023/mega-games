#include <bitset>
#include <random>
// Tile ID → Settlement IDs
#include <cstdint>
constexpr uint64_t tile_settlements[19] = {
    0x0000000000000707ULL, // Tile 1
    0x0000000000001C1CULL, // Tile 2
    0x0000000000007070ULL, // Tile 3
    0x00000000000E0380ULL, // Tile 4
    0x0000000000380E00ULL, // Tile 5
    0x0000000000E03800ULL, // Tile 6
    0x000000000380E000ULL, // Tile 7
    0x0000000038070000ULL, // Tile 8
    0x00000000E01C0000ULL, // Tile 9
    0x0000000380700000ULL, // Tile 10
    0x0000000E01C00000ULL, // Tile 11
    0x0000003807000000ULL, // Tile 12
    0x000001C070000000ULL, // Tile 13
    0x00000701C0000000ULL, // Tile 14
    0x00001C0700000000ULL, // Tile 15
    0x0000701C00000000ULL, // Tile 16
    0x0003838000000000ULL, // Tile 17
    0x000E0E0000000000ULL, // Tile 18
    0x0038380000000000ULL  // Tile 19
};

const uint8_t N_ROADS = 72;
const std::array<std::bitset<N_ROADS>, 54> settlement_roads = {
    std::bitset<N_ROADS>{0x41ULL},    // Settlement 1
    std::bitset<N_ROADS>{0x3ULL},     // 2
    std::bitset<N_ROADS>{0x86ULL},    // 3
    std::bitset<N_ROADS>{0xCULL},     // 4
    std::bitset<N_ROADS>{0x118ULL},   // 5
    std::bitset<N_ROADS>{0x30ULL},    // 6
    std::bitset<N_ROADS>{0x220ULL},   // 7
    std::bitset<N_ROADS>{0x40400ULL}, // 8
    std::bitset<N_ROADS>{0xC40ULL},   // 9
    std::bitset<N_ROADS>{0x81800ULL}, // 10
    std::bitset<N_ROADS>{0x3080ULL},
    std::bitset<N_ROADS>{0x106000ULL},
    std::bitset<N_ROADS>{0xC100ULL},
    std::bitset<N_ROADS>{0x218000ULL},
    std::bitset<N_ROADS>{0x30200ULL},
    std::bitset<N_ROADS>{0x420000ULL},
    std::bitset<N_ROADS>{0x200800000ULL},
    std::bitset<N_ROADS>{0x1840000ULL},
    std::bitset<N_ROADS>{0x403000000ULL},
    std::bitset<N_ROADS>{0x6080000ULL},
    std::bitset<N_ROADS>{0x80C000000ULL},
    std::bitset<N_ROADS>{0x18100000ULL},
    std::bitset<N_ROADS>{0x1030000000ULL},
    std::bitset<N_ROADS>{0x60200000ULL},
    std::bitset<N_ROADS>{0x20C0000000ULL},
    std::bitset<N_ROADS>{0x180400000ULL},
    std::bitset<N_ROADS>{0x4100000000ULL},
    std::bitset<N_ROADS>{0x8200000000ULL},
    std::bitset<N_ROADS>{0x2018000000000ULL},
    std::bitset<N_ROADS>{0x30400000000ULL},
    std::bitset<N_ROADS>{0x4060000000000ULL},
    std::bitset<N_ROADS>{0xC0800000000ULL},
    std::bitset<N_ROADS>{0x8180000000000ULL},
    std::bitset<N_ROADS>{0x301000000000ULL},
    std::bitset<N_ROADS>{0x10600000000000ULL},
    std::bitset<N_ROADS>{0xC02000000000ULL},
    std::bitset<N_ROADS>{0x21800000000000ULL},
    std::bitset<N_ROADS>{0x1004000000000ULL},
    std::bitset<N_ROADS>{0x42000000000000ULL},
    std::bitset<N_ROADS>{0x40C0000000000000ULL},
    std::bitset<N_ROADS>{0x184000000000000ULL},
    std::bitset<N_ROADS>{0x8300000000000000ULL},
    std::bitset<N_ROADS>{0x608000000000000ULL},
    std::bitset<N_ROADS>{0xC00000000000000ULL} | (std::bitset<N_ROADS>{0x1ULL} << 64),
    std::bitset<N_ROADS>{0x1810000000000000ULL},
    std::bitset<N_ROADS>{0x3000000000000000ULL} | (std::bitset<N_ROADS>{0x2ULL} << 64),
    std::bitset<N_ROADS>{0x2020000000000000ULL},
    std::bitset<N_ROADS>{0x4000000000000000ULL} | (std::bitset<N_ROADS>{0x4ULL} << 64),
    std::bitset<N_ROADS>{0xCULL} << 64,
    std::bitset<N_ROADS>{0x8000000000000000ULL} | (std::bitset<N_ROADS>{0x18ULL} << 64),
    std::bitset<N_ROADS>{0x30ULL} << 64,
    std::bitset<N_ROADS>{0x61ULL} << 64,
    std::bitset<N_ROADS>{0xC0ULL} << 64,
    std::bitset<N_ROADS>{0x82ULL} << 64 // Settlement 54
};

constexpr uint8_t road_to_settlements[72][2] = {
    { 1,  2}, { 2,  3}, { 3,  4}, { 4,  5}, { 5,  6}, { 6,  7}, // 1-6
    { 1,  9}, { 3, 11}, { 5, 13}, { 7, 15}, { 8,  9}, { 9, 10}, // 7-12
    {10, 11}, {11, 12}, {12, 13}, {13, 14}, {14, 15}, {15, 16}, // 13-18
    { 8, 18}, {10, 20}, {12, 22}, {14, 24}, {16, 26}, {17, 18}, // 19-24
    {18, 19}, {19, 20}, {20, 21}, {21, 22}, {22, 23}, {23, 24}, // 25-30
    {24, 25}, {25, 26}, {26, 27}, {17, 28}, {19, 30}, {21, 32}, // 31-36
    {23, 34}, {25, 36}, {27, 38}, {28, 29}, {29, 30}, {30, 31}, // 37-42
    {31, 32}, {32, 33}, {33, 34}, {34, 35}, {35, 36}, {36, 37}, // 43-48
    {37, 38}, {29, 39}, {31, 41}, {33, 43}, {35, 45}, {37, 47}, // 49-54
    {39, 40}, {40, 41}, {41, 42}, {42, 43}, {43, 44}, {44, 45}, // 55-60
    {45, 46}, {46, 47}, {40, 48}, {42, 50}, {44, 52}, {46, 54}, // 61-66
    {48, 49}, {49, 50}, {50, 51}, {51, 52}, {52, 53}, {53, 54}  // 67-72
};

constexpr uint8_t settlement_to_settlements[54][3] = {
    { 2,  9,  0}, { 1,  3,  0}, { 2,  4, 11}, { 3,  5,  0}, { 4,  6, 13}, { 5,  7,  0}, // 1-6
    { 6, 15,  0}, { 9, 18,  0}, { 1,  8, 10}, { 9, 11, 20}, { 3, 10, 12}, {11, 13, 22}, // 7-12
    { 5, 12, 14}, {13, 15, 24}, { 7, 14, 16}, {15, 26,  0}, {18, 28,  0}, { 8, 17, 19}, // 13-18
    {18, 20, 30}, {10, 19, 21}, {20, 22, 32}, {12, 21, 23}, {22, 24, 34}, {14, 23, 25}, // 19-24
    {24, 26, 36}, {16, 25, 27}, {26, 38,  0}, {17, 29,  0}, {28, 30, 39}, {19, 29, 31}, // 25-30
    {30, 32, 41}, {21, 31, 33}, {32, 34, 43}, {23, 33, 35}, {34, 36, 45}, {25, 35, 37}, // 31-36
    {36, 38, 47}, {27, 37,  0}, {29, 40,  0}, {39, 41, 48}, {31, 40, 42}, {41, 43, 50}, // 37-42
    {33, 42, 44}, {43, 45, 52}, {35, 44, 46}, {45, 47, 54}, {37, 46,  0}, {40, 49,  0}, // 43-48
    {48, 50,  0}, {42, 49, 51}, {50, 52,  0}, {44, 51, 53}, {52, 54,  0}, {46, 53,  0}  // 49-54
};

const uint8_t N_PLAYERS = 4;
enum PLAYER_COLOR {
    WHITE = 0,
    RED = 1,
    BLUE = 2,
    ORANGE = 3,
};

const uint8_t N_RESOURCES = 5;
enum RESOURCE_TYPE{
    WOOD = 0,
    WHEAT = 1,
    SHEEP = 2,
    CLAY = 3,
    STONE = 4
};
const uint8_t N_NUMBERS = 11;

const uint8_t N_DEV_CARDS = 5;
const uint8_t N_DEV_CARDS_TOTAL = 25;
enum DEV_CARD_TYPE {
    KNIGHT = 0,
    ROAD_DEV = 1,
    PLENTY = 2,
    MONOPOLY = 3,
    VP = 4
};

const uint8_t N_BUILD_TYPES = 4;
enum BUILD_TYPE {
    ROAD_BUILD = 0,
    SETTLEMENT = 1,
    CITY = 2,
    DEV_CARD = 3
};

constexpr uint8_t BUILDING_COSTS[N_BUILD_TYPES][N_RESOURCES]{
    {1,0,0,1,0},
    {1,1,1,1,0},
    {0,2,0,0,3},
    {0,1,1,0,1}
};

uint8_t THIEF_TILE;
std::mt19937 rng(std::random_device{}());

struct {
    std::array<std::array<uint8_t, N_RESOURCES>, N_PLAYERS> player_resources{};
    std::array<std::array<uint8_t, N_DEV_CARDS>, N_PLAYERS> player_dev_cards{};
    std::array<uint64_t, N_PLAYERS> settlements{};
    std::array<uint64_t, N_PLAYERS> cities{};
    std::array<std::bitset<N_ROADS>, N_PLAYERS> roads{} ;
    std::array<uint32_t, N_NUMBERS>  tile_numbers{};
    std::array<RESOURCE_TYPE, 19> tile_resources{};
    std::array<DEV_CARD_TYPE, N_DEV_CARDS_TOTAL> deck_dev_cards{};
    uint8_t deck_pointer = 0;
    std::array<uint8_t, N_PLAYERS> knight_cards{};
    std::array<uint8_t, N_PLAYERS> victory_points{};
    uint8_t longest_road = 4;
    PLAYER_COLOR longest_road_holder;
    uint8_t biggest_army = 2;
    PLAYER_COLOR biggest_army_holder;
} GAMESTATE;

bool buy(PLAYER_COLOR player, BUILD_TYPE build) {
    const uint8_t* necessary = BUILDING_COSTS[build];
    for (int i = 0; i < N_RESOURCES; i++) {
        if (GAMESTATE.player_resources[player][i] < necessary[i]) {
            return false;
        }
    }
    GAMESTATE.player_resources[player][WOOD] -= necessary[WOOD];
    GAMESTATE.player_resources[player][WHEAT]-= necessary[WHEAT];
    GAMESTATE.player_resources[player][SHEEP]-= necessary[SHEEP];
    GAMESTATE.player_resources[player][CLAY]-= necessary[CLAY];
    GAMESTATE.player_resources[player][STONE]-= necessary[STONE];
    return true;
}
