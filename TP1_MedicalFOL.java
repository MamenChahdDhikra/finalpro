import org.tweetyproject.logics.fol.syntax.*;
import org.tweetyproject.logics.fol.parser.*;
import org.tweetyproject.logics.commons.syntax.*;
import org.tweetyproject.logics.commons.syntax.interfaces.*;
import org.tweetyproject.logics.fol.reasoner.*;

public class TP1_MedicalFOL {

    public static void main(String[] args) throws Exception {

        // === 1. Créer la Signature ===
        FolSignature sig = new FolSignature(true);

        // Prédicats (nom, nombre d'arguments)
        Predicate aFievre   = new Predicate("aFievre", 1);
        Predicate aToux     = new Predicate("aToux", 1);
        Predicate aGrippe   = new Predicate("aGrippe", 1);
        Predicate estMalade = new Predicate("estMalade", 1);

        sig.add(aFievre);
        sig.add(aToux);
        sig.add(aGrippe);
        sig.add(estMalade);

        // Constantes (patients)
        Constant alice = new Constant("alice");
        Constant bob   = new Constant("bob");
        Constant sara  = new Constant("sara");

        sig.add(alice);
        sig.add(bob);
        sig.add(sara);

        // === 2. Parser ===
        FolParser parser = new FolParser();
        parser.setSignature(sig);

        // === 3. Base de Connaissances ===
        FolBeliefSet kb = new FolBeliefSet();

        // Règle 1: si quelqu'un a fièvre ET toux → il a la grippe
        kb.add((FolFormula) parser.parseFormula(
            "forall X: (aFievre(X) && aToux(X) => aGrippe(X))"));

        // Règle 2: si quelqu'un a la grippe → il est malade
        kb.add((FolFormula) parser.parseFormula(
            "forall X: (aGrippe(X) => estMalade(X))"));

        // Faits sur Alice: elle a fièvre et toux
        kb.add((FolFormula) parser.parseFormula("aFievre(alice)"));
        kb.add((FolFormula) parser.parseFormula("aToux(alice)"));

        // Faits sur Bob: il a seulement la toux
        kb.add((FolFormula) parser.parseFormula("aToux(bob)"));

        // Faits sur Sara: elle a la grippe directement
        kb.add((FolFormula) parser.parseFormula("aGrippe(sara)"));

        // === 4. Afficher la base ===
        System.out.println("=== Base de Connaissances Medicale ===");
        for (FolFormula f : kb) {
            System.out.println("  " + f);
        }

        // === 5. Raisonnement ===
        System.out.println("\n=== Requetes ===");

        SimpleFolReasoner reasoner = new SimpleFolReasoner();

        // Alice a-t-elle la grippe ?
        FolFormula q1 = (FolFormula) parser.parseFormula("aGrippe(alice)");
        System.out.println("Alice a la grippe ?   " 
            + reasoner.query(kb, q1));

        // Alice est-elle malade ?
        FolFormula q2 = (FolFormula) parser.parseFormula("estMalade(alice)");
        System.out.println("Alice est malade ?    " 
            + reasoner.query(kb, q2));

        // Bob a-t-il la grippe ?
        FolFormula q3 = (FolFormula) parser.parseFormula("aGrippe(bob)");
        System.out.println("Bob a la grippe ?     " 
            + reasoner.query(kb, q3));

        // Bob est-il malade ?
        FolFormula q4 = (FolFormula) parser.parseFormula("estMalade(bob)");
        System.out.println("Bob est malade ?      " 
            + reasoner.query(kb, q4));

        // Sara est-elle malade ?
        FolFormula q5 = (FolFormula) parser.parseFormula("estMalade(sara)");
        System.out.println("Sara est malade ?     " 
            + reasoner.query(kb, q5));
    }
}
