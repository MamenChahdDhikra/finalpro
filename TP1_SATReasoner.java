import java.util.*;

public class TP1_SATReasoner {

    // قاعدة المعرفة - كل clause هي قائمة من الليترالات
    static List<List<Integer>> kb = new ArrayList<>();

    public static void main(String[] args) {

        // === قاعدة معرفة Céphalopodes ===
        // المتغيرات:
        // 1=mollusque, 2=cephalopode, 3=tentacules, 4=encre, 5=vertebre

        // cephalopode → mollusque : (-2 ∨ 1)
        kb.add(Arrays.asList(-2, 1));
        // cephalopode → tentacules : (-2 ∨ 3)
        kb.add(Arrays.asList(-2, 3));
        // cephalopode → encre : (-2 ∨ 4)
        kb.add(Arrays.asList(-2, 4));
        // cephalopode → ¬vertebre : (-2 ∨ -5)
        kb.add(Arrays.asList(-2, -5));
        // Fait: cephalopode = vrai
        kb.add(Arrays.asList(2));

        System.out.println("=== Raisonnement par l'absurde ===\n");

        // BC |= mollusque (1) ?
        System.out.println("BC |= mollusque ?   " + entails(1));
        // BC |= tentacules (3) ?
        System.out.println("BC |= tentacules ?  " + entails(3));
        // BC |= encre (4) ?
        System.out.println("BC |= encre ?       " + entails(4));
        // BC |= ¬vertebre (-5) ?
        System.out.println("BC |= ¬vertebre ?   " + entails(-5));
        // BC |= vertebre (5) ? → doit etre false
        System.out.println("BC |= vertebre ?    " + entails(5));
    }

    // BC |= φ  ⟺  BC ∪ {¬φ} est UNSATISFIABLE
    static boolean entails(int literal) {
        List<List<Integer>> bcNeg = new ArrayList<>(kb);
        // Ajouter ¬φ
        bcNeg.add(Arrays.asList(-literal));
        // Si UNSAT → BC infère φ
        boolean unsat = !dpll(bcNeg, new HashMap<>());
        return unsat;
    }

    // Algorithme DPLL
    static boolean dpll(List<List<Integer>> clauses,
                        Map<Integer, Boolean> assignment) {

        // 1. Toutes les clauses satisfaites ?
        if (allSatisfied(clauses, assignment)) return true;

        // 2. Clause vide → contradiction
        if (hasEmptyClause(clauses, assignment)) return false;

        // 3. Unit Propagation
        for (List<Integer> clause : clauses) {
            List<Integer> unassigned = getUnassigned(clause, assignment);
            if (unassigned.size() == 1) {
                int lit = unassigned.get(0);
                Map<Integer, Boolean> newAssign = new HashMap<>(assignment);
                newAssign.put(Math.abs(lit), lit > 0);
                return dpll(clauses, newAssign);
            }
        }

        // 4. Choisir une variable et tester true/false
        int var = chooseVar(clauses, assignment);
        if (var == 0) return false;

        Map<Integer, Boolean> tryTrue = new HashMap<>(assignment);
        tryTrue.put(var, true);
        if (dpll(clauses, tryTrue)) return true;

        Map<Integer, Boolean> tryFalse = new HashMap<>(assignment);
        tryFalse.put(var, false);
        return dpll(clauses, tryFalse);
    }

    // Vérifie si toutes les clauses sont satisfaites
    static boolean allSatisfied(List<List<Integer>> clauses,
                                 Map<Integer, Boolean> assignment) {
        for (List<Integer> clause : clauses) {
            boolean sat = false;
            for (int lit : clause) {
                int var = Math.abs(lit);
                if (assignment.containsKey(var)) {
                    boolean val = assignment.get(var);
                    if ((lit > 0 && val) || (lit < 0 && !val)) {
                        sat = true;
                        break;
                    }
                }
            }
            if (!sat) return false;
        }
        return true;
    }

    // Vérifie s'il existe une clause vide (contradiction)
    static boolean hasEmptyClause(List<List<Integer>> clauses,
                                   Map<Integer, Boolean> assignment) {
        for (List<Integer> clause : clauses) {
            boolean allFalse = true;
            for (int lit : clause) {
                int var = Math.abs(lit);
                if (!assignment.containsKey(var)) {
                    allFalse = false;
                    break;
                }
                boolean val = assignment.get(var);
                if ((lit > 0 && val) || (lit < 0 && !val)) {
                    allFalse = false;
                    break;
                }
            }
            if (allFalse) return true;
        }
        return false;
    }

    // Retourne les littéraux non assignés d'une clause
    static List<Integer> getUnassigned(List<Integer> clause,
                                        Map<Integer, Boolean> assignment) {
        List<Integer> result = new ArrayList<>();
        for (int lit : clause) {
            if (!assignment.containsKey(Math.abs(lit))) {
                result.add(lit);
            }
        }
        return result;
    }

    // Choisit la première variable non assignée
    static int chooseVar(List<List<Integer>> clauses,
                          Map<Integer, Boolean> assignment) {
        for (List<Integer> clause : clauses) {
            for (int lit : clause) {
                if (!assignment.containsKey(Math.abs(lit))) {
                    return Math.abs(lit);
                }
            }
        }
        return 0;
    }
}
