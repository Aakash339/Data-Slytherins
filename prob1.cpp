// Maze with Keys and Doors
// Build : g++ -std=c++17 -O2 maze_keys_doors.cpp -o maze
// Run   : ./maze
//
// Algorithm: BFS over states (row, col, keyMask). keyMask has 6 bits (a-f).
// Complexity: O(N^2 * 2^6) time and memory.
#include <bits/stdc++.h>
using namespace std;

typedef vector<string> Grid;
static const int MASKS = 64;                 // 2^6 key combinations
static const int DR[4] = {-1, 1, 0, 0};
static const int DC[4] = {0, 0, -1, 1};

// NOTE: the problem says doors are 'A'-'F', but 'E' is also the exit symbol.
// To remove the clash, 'E' is ALWAYS the exit, and the door that matches key 'e'
// is written as 'G'. So door letters are  A B C D G F  <->  keys a b c d e f.
static const char DOOR_CHARS[7] = "ABCDGF";
inline int keyIdx(char ch)  { return (ch >= 'a' && ch <= 'f') ? ch - 'a' : -1; }
inline int doorIdx(char ch) {
    for (int i = 0; i < 6; i++) if (ch == DOOR_CHARS[i]) return i;
    return -1;
}

struct Result {
    int dist = -1;
    vector<pair<int,int>> path;              // cells from S to E (inclusive)
};

// ---------------------------------------------------------------- solver
Result solve(const Grid& g) {
    int N = g.size(), sr = -1, sc = -1;
    for (int r = 0; r < N; r++)
        for (int c = 0; c < N; c++)
            if (g[r][c] == 'S') { sr = r; sc = c; }
    Result res;
    if (sr < 0) return res;

    vector<int> dist(N * N * MASKS, -1), par(N * N * MASKS, -1);
    queue<int> q;
    int start = (sr * N + sc) * MASKS;
    dist[start] = 0;
    q.push(start);

    while (!q.empty()) {
        int s = q.front(); q.pop();
        int mask = s % MASKS, cell = s / MASKS;
        int r = cell / N, c = cell % N;

        if (g[r][c] == 'E') {                // first time reaching E = shortest
            res.dist = dist[s];
            for (int cur = s; cur != -1; cur = par[cur]) {
                int cc = cur / MASKS;
                res.path.push_back({cc / N, cc % N});
            }
            reverse(res.path.begin(), res.path.end());
            return res;
        }
        for (int d = 0; d < 4; d++) {
            int nr = r + DR[d], nc = c + DC[d];
            if (nr < 0 || nc < 0 || nr >= N || nc >= N) continue;
            char ch = g[nr][nc];
            if (ch == '#') continue;
            int di = doorIdx(ch);
            if (di >= 0 && !((mask >> di) & 1)) continue;                         // locked door
            int nm = mask;
            if (keyIdx(ch) >= 0) nm |= 1 << keyIdx(ch);                           // pick key
            int ns = (nr * N + nc) * MASKS + nm;
            if (dist[ns] != -1) continue;
            dist[ns] = dist[s] + 1;
            par[ns] = s;
            q.push(ns);
        }
    }
    return res;                              // dist = -1
}

// ---------------------------------------------------------------- CSV I/O
static string trim(const string& s) {
    size_t a = s.find_first_not_of(" \t\r\n"), b = s.find_last_not_of(" \t\r\n");
    return a == string::npos ? "" : s.substr(a, b - a + 1);
}

bool readCSV(const string& file, Grid& g) {
    ifstream in(file);
    if (!in) { cerr << "Cannot open file: " << file << "\n"; return false; }
    string line;
    g.clear();
    while (getline(in, line)) {
        line = trim(line);
        if (line.empty()) continue;
        string row;
        if (line.find(',') == string::npos) row = line;      // also accept "S..#E"
        else {
            stringstream ss(line);
            string tok;
            while (getline(ss, tok, ',')) {
                tok = trim(tok);
                row += tok.empty() ? '.' : tok[0];
            }
        }
        g.push_back(row);
    }
    int N = g.size();
    if (N == 0) { cerr << "Empty grid\n"; return false; }
    for (auto& r : g)
        if ((int)r.size() != N) { cerr << "Grid is not N x N\n"; return false; }
    int s = 0, e = 0;
    for (auto& r : g) for (char ch : r) { s += ch == 'S'; e += ch == 'E'; }
    if (s != 1 || e != 1) { cerr << "Grid needs exactly one 'S' and one 'E'\n"; return false; }
    return true;
}

void writeCSV(const string& file, const Grid& g) {
    ofstream out(file);
    for (auto& row : g) {
        for (size_t i = 0; i < row.size(); i++) out << row[i] << (i + 1 < row.size() ? "," : "");
        out << "\n";
    }
}

// "tests/test1.csv" -> "tests/test1"  (strip the .csv extension)
string stripExt(const string& f) {
    size_t dot = f.rfind('.'), slash = f.find_last_of("/\\");
    if (dot == string::npos || (slash != string::npos && dot < slash)) return f;
    return f.substr(0, dot);
}

// ---------------------------------------------------------------- random maze
bool generateMaze(int N, int T, unsigned seed, Grid& g) {
    if (N * N < 2 + 2 * T) { cerr << "Grid too small for T keys + T doors\n"; return false; }
    mt19937 rng(seed);
    double wallProb = 0.30;
    for (int attempt = 1; attempt <= 5000; attempt++) {
        if (attempt % 250 == 0 && wallProb > 0.05) wallProb -= 0.05;   // relax if unlucky
        g.assign(N, string(N, '.'));
        uniform_real_distribution<double> U(0, 1);
        for (int r = 0; r < N; r++)
            for (int c = 0; c < N; c++)
                if (U(rng) < wallProb) g[r][c] = '#';

        vector<int> cells(N * N);
        iota(cells.begin(), cells.end(), 0);
        shuffle(cells.begin(), cells.end(), rng);
        int k = 0;
        auto put = [&](char ch) { int p = cells[k++]; g[p / N][p % N] = ch; };
        put('S'); put('E');
        for (int i = 0; i < T; i++) { put('a' + i); put(DOOR_CHARS[i]); }

        Result r = solve(g);
        if (r.dist != -1) return true;                  // solvable maze found
    }
    return false;
}

// ---------------------------------------------------------------- visualisation
// colour per key/door pair (256-colour ANSI) and (R,G,B) for HTML
static const int ANSI_PAIR[6]   = {208, 129, 33, 226, 205, 94};
static const char* HTML_PAIR[6] = {"#ff9800", "#9c27b0", "#2196f3", "#ffeb3b", "#ff69b4", "#8d6e63"};

void printColoured(const Grid& g, const set<pair<int,int>>& path) {
    int N = g.size();
    for (int r = 0; r < N; r++) {
        for (int c = 0; c < N; c++) {
            char ch = g[r][c];
            bool onPath = path.count({r, c}) > 0;
            string bg, fg = "\033[30m", txt = "  ";
            if (ch == '#')      { bg = "\033[40m"; }
            else if (ch == 'S') { bg = "\033[42m"; txt = "S "; }
            else if (ch == 'E') { bg = "\033[41m"; txt = "E "; fg = "\033[97m"; }
            else if (keyIdx(ch) >= 0 || doorIdx(ch) >= 0) {
                int id = keyIdx(ch) >= 0 ? keyIdx(ch) : doorIdx(ch);
                bg = "\033[48;5;" + to_string(ANSI_PAIR[id]) + "m"; txt = string(1, ch) + " ";
            }
            else if (onPath)    { bg = "\033[46m"; txt = "x "; }       // highlighted path
            else                { bg = "\033[107m"; }                  // white
            string bold = (onPath && ch != '.' && ch != 'S' && ch != 'E') ? "\033[1;4m" : "";
            cout << bg << fg << bold << txt << "\033[0m";
        }
        cout << "\n";
    }
    cout << "Legend: white=open, black=wall, green=S, red=E, cyan(x)=path, "
            "coloured letters=key/door pairs (bold+underlined if used on path)\n";
}

void writeHTML(const string& file, const Grid& g, const set<pair<int,int>>& path, int dist) {
    int N = g.size();
    ofstream o(file);
    o << "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Maze</title><style>"
         "body{font-family:sans-serif}table{border-collapse:collapse}"
         "td{width:36px;height:36px;text-align:center;font-weight:bold;border:1px solid #888}"
         ".p{outline:3px solid #00bcd4;outline-offset:-3px}</style></head><body>";
    o << "<h3>Shortest path length: " << dist << "</h3><table>";
    for (int r = 0; r < N; r++) {
        o << "<tr>";
        for (int c = 0; c < N; c++) {
            char ch = g[r][c];
            bool onPath = path.count({r, c}) > 0;
            string bg = "#fff", color = "#000", txt = "";
            if (ch == '#') bg = "#000";
            else if (ch == 'S') { bg = "#4caf50"; txt = "S"; }
            else if (ch == 'E') { bg = "#f44336"; txt = "E"; color = "#fff"; }
            else if (keyIdx(ch) >= 0 || doorIdx(ch) >= 0) {
                bg = HTML_PAIR[keyIdx(ch) >= 0 ? keyIdx(ch) : doorIdx(ch)]; txt = string(1, ch);
            }
            else if (onPath) { bg = "#80deea"; txt = "x"; }
            o << "<td class='" << (onPath ? "p" : "") << "' style='background:" << bg
              << ";color:" << color << "'>" << txt << "</td>";
        }
        o << "</tr>";
    }
    o << "</table><p>White=open, Black=wall, Green=S, Red=E, "
         "each key/door pair has its own colour, cyan outline = path taken.</p></body></html>";
}

// ---------------------------------------------------------------- main
int main() {
    int T, option;
    cout << "Enter T (number of key/door types, 1..6): ";
    if (!(cin >> T) || T < 1 || T > 6) { cerr << "Invalid T\n"; return 1; }
    cout << "Option 1: read grid from CSV\nOption 2: generate random maze\nChoose: ";
    cin >> option;

    Grid g;
    string baseName;                                   // used to name the output files
    if (option == 1) {
        string file;
        cout << "CSV file name: ";
        cin >> file;
        if (!readCSV(file, g)) return 1;
        baseName = stripExt(file);
    } else if (option == 2) {
        int N; unsigned seed;
        cout << "Grid size N: ";
        cin >> N;
        cout << "Random seed (0 = time based): ";
        cin >> seed;
        if (seed == 0) seed = (unsigned)time(nullptr);
        if (!generateMaze(N, T, seed, g)) { cerr << "Could not generate a solvable maze\n"; return 1; }
        writeCSV("generated_maze.csv", g);
        baseName = "generated_maze";
        cout << "Generated maze saved to generated_maze.csv (seed " << seed << ")\n";
    } else { cerr << "Invalid option\n"; return 1; }

    Result res = solve(g);

    // Output 1
    cout << "\nShortest path length: " << res.dist << "\n\n";

    // Output 2: mark path with 'x' (only on open cells, so keys/doors/S/E stay identifiable)
    Grid out = g;
    set<pair<int,int>> pathSet(res.path.begin(), res.path.end());
    for (auto& p : res.path)
        if (out[p.first][p.second] == '.') out[p.first][p.second] = 'x';
    string outFile = baseName + "_output.csv";          // separate output CSV
    {
        cout << "Output CSV name [" << outFile << "] (press Enter for default): ";
        string custom;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(cin, custom);
        custom = trim(custom);
        if (!custom.empty()) outFile = custom;
    }
    if (res.dist != -1) writeCSV(outFile, out);
    else cout << "No path exists, so no output CSV was written.\n";

    // Visualisation
    printColoured(g, pathSet);
    string htmlFile = baseName + "_maze.html";
    writeHTML(htmlFile, g, pathSet, res.dist);
    cout << "\nFiles written: " << (res.dist != -1 ? outFile + ", " : "") << htmlFile << "\n";
    return 0;
}