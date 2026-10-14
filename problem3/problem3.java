import java.awt.*;
import java.awt.geom.*;
import java.io.*;
import java.util.*;
import java.util.List;
import javax.swing.*;

public class problem3 {
    static class F { int u, v, p; boolean path, coup;
        F(int u, int v, int p) { this.u = u; this.v = v; this.p = p; }
        int paid() { return coup ? p / 2 : p; } }

    static int n, K, C, cost = -1;
    static List<F> fl = new ArrayList<>(), route = new ArrayList<>();
    static final Color GR = new Color(46, 170, 70), RD = new Color(215, 55, 55), OR = new Color(255, 152, 0),
            GD = new Color(240, 180, 0), BL = new Color(90, 140, 230);

    // DP: d[e][c][v] = min cost to reach v with e flights and c coupons (at most K+1 flights)
    static void solve() {
        if (n == 1) { cost = 0; return; }
        int INF = 1 << 29, E = K + 1;
        int[][][] d = new int[E + 1][C + 1][n + 1], pr = new int[E + 1][C + 1][n + 1];
        for (int[][] a : d) for (int[] b : a) Arrays.fill(b, INF);
        d[0][0][1] = 0;
        for (int e = 0; e < E; e++) for (int c = 0; c <= C; c++) for (int i = 0; i < fl.size(); i++) {
            F f = fl.get(i); int x = d[e][c][f.u];
            if (x >= INF) continue;
            for (int k = 0; k < 2 && c + k <= C; k++) {
                int nd = x + (k == 1 ? f.p / 2 : f.p);
                if (nd < d[e + 1][c + k][f.v]) { d[e + 1][c + k][f.v] = nd; pr[e + 1][c + k][f.v] = i * 2 + k; }
            }
        }
        int be = 0, bc = 0, best = INF;
        for (int e = 1; e <= E; e++) for (int c = 0; c <= C; c++) if (d[e][c][n] < best) { best = d[e][c][n]; be = e; bc = c; }
        if (best >= INF) return;
        cost = best;
        for (int v = n, e = be, c = bc; e > 0; e--) {
            int q = pr[e][c][v]; F f = fl.get(q / 2);
            f.path = true; f.coup = q % 2 == 1; route.add(0, f); v = f.u; c -= q % 2;
        }
    }

    // random graph with a guaranteed 1 -> n route using <= K stops
    static void gen() {
        Random r = new Random(); Set<Integer> s = new HashSet<>(); List<Integer> mid = new ArrayList<>();
        for (int i = 2; i < n; i++) mid.add(i);
        Collections.shuffle(mid);
        int len = Math.min(K + 1, n - 1), a = 1;
        for (int i = 0; i < len; i++) { int b = i == len - 1 ? n : mid.get(i); fl.add(new F(a, b, 20 + r.nextInt(180))); s.add(a * 10000 + b); a = b; }
        for (int t = 0; t < 20 * n && fl.size() < Math.min(3 * n, n * (n - 1)); t++) {
            int u = 1 + r.nextInt(n), v = 1 + r.nextInt(n);
            if (u != v && s.add(u * 10000 + v)) fl.add(new F(u, v, 10 + r.nextInt(190)));
        }
        Collections.shuffle(fl);
    }

    static class P extends JPanel {
        static final int R = 16;
        int tr, pause = 40, run, cu; double t; boolean mv;
        JLabel st = new JLabel(" ", SwingConstants.CENTER), dt = new JLabel(" ", SwingConstants.CENTER);
        javax.swing.Timer tm = new javax.swing.Timer(16, e -> tick());

        P() { setBackground(Color.WHITE);
            if (cost < 0) st.setText("No route within " + K + " stops -> -1"); else { info(); tm.start(); } }

        void reset() { tr = run = cu = 0; pause = 40; mv = false; info(); dt.setText(" "); tm.start(); }

        void info() { st.setText("Running cost: " + run + "  |  Stops used: " + Math.max(0, tr == route.size() ? tr - 1 : tr)
                + "/" + K + "  |  Coupons used: " + cu + "/" + C); }

        void tick() {
            if (pause > 0) { pause--; return; }
            if (tr >= route.size()) { dt.setText("Arrived! Minimum cost = " + cost); tm.stop(); return; }
            F f = route.get(tr);
            if (!mv) { mv = true; t = 0;
                dt.setText("Flight " + f.u + " -> " + f.v + ": " + (f.coup ? "COUPON applied! " + f.p + " -> " + f.p / 2 : "price " + f.p)); }
            if ((t += .025) >= 1) { mv = false; run += f.paid(); cu += f.coup ? 1 : 0; tr++; pause = 25; info(); }
            repaint();
        }

        Point2D pos(int i) { double r = Math.min(getWidth(), getHeight()) / 2. - 60, a = 2 * Math.PI * (i - 1) / n - Math.PI / 2;
            return new Point2D.Double(getWidth() / 2. + r * Math.cos(a), getHeight() / 2. + r * Math.sin(a)); }

        Point2D cut(Point2D p, double x, double y) { double dx = x - p.getX(), dy = y - p.getY(), l = Math.hypot(dx, dy);
            return new Point2D.Double(p.getX() + dx / l * R, p.getY() + dy / l * R); }

        QuadCurve2D q(F f) { Point2D a = pos(f.u), b = pos(f.v);
            double dx = b.getX() - a.getX(), dy = b.getY() - a.getY();
            double cx = (a.getX() + b.getX()) / 2 - dy * .15, cy = (a.getY() + b.getY()) / 2 + dx * .15;
            Point2D s = cut(a, cx, cy), e = cut(b, cx, cy);
            return new QuadCurve2D.Double(s.getX(), s.getY(), cx, cy, e.getX(), e.getY()); }

        Point2D at(QuadCurve2D q, double s) { double m = 1 - s;
            return new Point2D.Double(m * m * q.getX1() + 2 * m * s * q.getCtrlX() + s * s * q.getX2(),
                    m * m * q.getY1() + 2 * m * s * q.getCtrlY() + s * s * q.getY2()); }

        void arrow(Graphics2D g, QuadCurve2D q) { double a = Math.atan2(q.getY2() - q.getCtrlY(), q.getX2() - q.getCtrlX());
            for (int s = -1; s <= 1; s += 2)
                g.draw(new Line2D.Double(q.getX2(), q.getY2(), q.getX2() - 10 * Math.cos(a + s * .4), q.getY2() - 10 * Math.sin(a + s * .4))); }

        @Override protected void paintComponent(Graphics g0) {
            super.paintComponent(g0);
            Graphics2D g = (Graphics2D) g0;
            g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
            for (F f : fl) {
                if (f.u == f.v) continue;
                int i = route.indexOf(f); boolean on = i >= 0 && (i < tr || i == tr && mv);
                QuadCurve2D c = q(f);
                g.setColor(i < 0 ? Color.LIGHT_GRAY : !on ? BL : f.coup ? GD : GR);
                g.setStroke(new BasicStroke(i < 0 ? 1 : on ? 4 : 2)); g.draw(c);
                g.setStroke(new BasicStroke(1)); arrow(g, c);
                Point2D m = at(c, .5);
                g.setColor(i < 0 ? Color.GRAY : Color.BLACK);
                g.drawString(on && f.coup ? f.p + " -> " + f.p / 2 : "" + f.p, (float) m.getX() - 8, (float) m.getY() - 3);
            }
            if (mv && tr < route.size()) { Point2D p = at(q(route.get(tr)), t); g.setColor(Color.BLACK); g.fillOval((int) p.getX() - 6, (int) p.getY() - 6, 12, 12); }
            Set<Integer> seen = new HashSet<>();
            for (int j = 0; j < tr; j++) seen.add(route.get(j).v);
            for (int i = 1; i <= n; i++) {
                Point2D p = pos(i); int x = (int) p.getX(), y = (int) p.getY();
                g.setColor(i == 1 ? GR : i == n ? RD : seen.contains(i) ? OR : new Color(225, 232, 245));
                g.fillOval(x - R, y - R, 2 * R, 2 * R);
                g.setColor(Color.DARK_GRAY); g.drawOval(x - R, y - R, 2 * R, 2 * R);
                g.setColor(i == 1 || i == n ? Color.WHITE : Color.BLACK);
                g.drawString("" + i, x - g.getFontMetrics().stringWidth("" + i) / 2, y + 5);
            }
        }
    }

    static void gui() {
        SwingUtilities.invokeLater(() -> {
            JFrame fr = new JFrame("Budget Traveller with Coupons"); fr.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            P p = new P();
            JPanel top = new JPanel(new GridLayout(2, 1)); top.add(p.st); top.add(p.dt);
            JButton b = new JButton("Replay"); b.addActionListener(e -> p.reset());
            JPanel bot = new JPanel(); bot.add(b);
            bot.add(new JLabel("<html><font color=green>green=start</font> <font color=red>red=destination</font> "
                    + "<font color=orange>orange=stop</font> <font color=#c89600>gold=coupon flight</font></html>"));
            fr.add(top, BorderLayout.NORTH); fr.add(p); fr.add(bot, BorderLayout.SOUTH);
            fr.setSize(950, 750); fr.setVisible(true);
        });
    }

    public static void main(String[] args) throws Exception {
        Scanner s = new Scanner(System.in);
        System.out.print("Option (1=manual, 2=CSV, 3=generate): ");
        int o = s.nextInt();
        if (o == 1) {
            System.out.println("Enter N M, then K C, then M lines: u v p");
            n = s.nextInt(); int m = s.nextInt(); K = s.nextInt(); C = s.nextInt();
            while (m-- > 0) fl.add(new F(s.nextInt(), s.nextInt(), s.nextInt()));
        } else {
            System.out.print("Enter K C: "); K = s.nextInt(); C = s.nextInt();
            if (o == 2) {
                System.out.print("CSV path: ");
                for (String l : java.nio.file.Files.readAllLines(java.nio.file.Path.of(s.next()))) {
                    String[] p = l.trim().split(",");
                    try { fl.add(new F(Integer.parseInt(p[0].trim()), Integer.parseInt(p[1].trim()), Integer.parseInt(p[2].trim()))); }
                    catch (Exception e) { /* header or bad row */ }
                }
                for (F f : fl) n = Math.max(n, Math.max(f.u, f.v));
            } else { System.out.print("Number of cities N: "); n = Math.max(2, s.nextInt()); gen(); }
        }
        fl.removeIf(f -> f.u < 1 || f.u > n || f.v < 1 || f.v > n);
        if (n < 1) { System.out.println(-1); return; }

        solve();
        System.out.println("Minimum cost: " + cost);
        for (F f : route) System.out.println("  " + f.u + " -> " + f.v + "  price " + f.p + (f.coup ? "  [coupon: " + f.p + " -> " + f.p / 2 + "]" : ""));

        try (PrintWriter w = new PrintWriter("output_path.csv")) {
            w.println("u,v,price,path,coupon,paid");
            for (F f : fl) w.println(f.u + "," + f.v + "," + f.p + "," + (f.path ? "x" : "") + "," + (f.path && f.coup ? "x" : "") + "," + (f.path ? "" + f.paid() : ""));
        }
        System.out.println("Wrote output_path.csv");
        if (!GraphicsEnvironment.isHeadless()) gui();
    }
}