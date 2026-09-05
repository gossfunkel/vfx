#include "raylib.h"
#include "raymath.h"
#include <iostream>
#include <vector>

#define TAU (M_PI*2.f)

#define SCREEN_WIDTH 800
#define SCREEN_HEIGHT 800

#define CELL_LENGTH 80
#define VERT_SIZE 6
#define TICKS_PER_SEC 10.

typedef struct {
    bool lit;
    double time_on;
    Color col;
    Vector2 pos;
} Node;

typedef struct {
    bool lit;
    double time_on;
    Vector2 tip_a;
    Vector2 tip_b;
} Edge;

int main() {
    InitWindow(SCREEN_WIDTH, SCREEN_HEIGHT, "blinky");
    SetRandomSeed(420);

    std::vector<Vector2> positions;

    std::vector<Node> nodes;
    for (size_t row = CELL_LENGTH/2; row < SCREEN_HEIGHT; row += CELL_LENGTH)
        for (size_t col = CELL_LENGTH/2; col < SCREEN_WIDTH; col += CELL_LENGTH)
            nodes.emplace_back(
                Node {
                    false, 0.f,
                    Color{GetRandomValue(0,255),GetRandomValue(0,255),GetRandomValue(0,255),0},
                    Vector2{(float)col,(float)row}
                }
            );

    std::vector<Edge> edges;
    for (auto node : nodes) {
        edges.emplace_back(
            Edge {
                false, 0.f,
                Vector2Subtract(node.pos, Vector2{VERT_SIZE+2.f,0.f}),
                Vector2Subtract(node.pos, Vector2{CELL_LENGTH-VERT_SIZE-2.f})
            }
        );
        edges.emplace_back(
            Edge {
                false, 0.f,
                Vector2Subtract(node.pos, Vector2{0.f,VERT_SIZE+2.f}),
                Vector2Subtract(node.pos, Vector2{0.f,CELL_LENGTH-VERT_SIZE-2.f})
            }
        );
    }

    double dt = 0.f;
    double time = 0.f;

    while(!WindowShouldClose()) {
        dt = GetFrameTime();

        if (floor(TICKS_PER_SEC * (time + dt)) > floor(TICKS_PER_SEC * time)) {
            nodes.at(GetRandomValue(0,nodes.size()-1)).lit = true;
            edges.at(GetRandomValue(0,edges.size()-1)).lit = true;
        }

        time += dt;

        for (std::vector<Node>::iterator node = nodes.begin(); node != nodes.end(); node++) {
            if (node->lit) {
                node->time_on += dt;
                if (node->time_on > 2.) {
                    node->lit = false;
                    node->time_on = 0.;
                }
            }
        }

        for (std::vector<Edge>::iterator edge = edges.begin(); edge != edges.end(); edge++) {
            if (edge->lit) {
                edge->time_on += dt;
                if (edge->time_on > 2.) {
                    edge->lit = false;
                    edge->time_on = 0.;
                }
            }
        }

    	BeginDrawing();
    		ClearBackground(BLACK);

            for (auto node : nodes)
                if (node.lit) {
                    node.col.a = floor(255. * (std::min(node.time_on, 1.) - (std::max(1., node.time_on)-1.)));
                    DrawCircleV(node.pos,VERT_SIZE,node.col);
                }

            for (auto edge : edges) {
                if (edge.lit) {
                    int col_val = floor(255. * (std::min(edge.time_on, 1.) - (std::max(1., edge.time_on)-1.)));
                    DrawLineV(edge.tip_a, edge.tip_b, Color{255,255,255,col_val});
                    //DrawLineV(edge.tip_a, edge.tip_b, WHITE);
                }
            }

    	EndDrawing();
    }
    CloseWindow();
    return 0;
}