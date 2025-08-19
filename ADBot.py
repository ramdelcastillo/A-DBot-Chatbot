from pyswip import Prolog

class ADBot:
    def __init__(self, kbPath="familyRelationships_KB.pl"):
        self.prolog = Prolog()
        self.prolog.consult(kbPath)
        self.learnedSomethingMessage = "A-DBot > OK! I learned something."
        self.impossibleMessage = "A-DBot > That's impossible!"
        self.debugMode = True
        print("A-DBot loaded and ready!")

    def printResponse(self, response: str, debugMessage: str = None):
        if self.debugMode and debugMessage:
            print(f"{response} ({debugMessage})")
        else:
            print(response)

    def printResponse2(self, response: str, debugMessage: str = None):
        if self.debugMode and debugMessage:
            print("A-DBot > " + f"{response} ({debugMessage})")
        else:
            print("A-DBot > " + response)

    def commandTokenizer(self, command):
        return command.strip().replace('.', '').replace('?', '').split()

    def isValidName(self, name):
        return name.isalpha() and name[0].isupper() and name[1:].islower()

    def haveSharedParent(self, person1, person2):
        try:
            query = f"parent(P, {person1}), parent(P, {person2}), {person1} \\= {person2}"
            results = list(self.prolog.query(query))
            return bool(results)
        except Exception:
            return False

    def hasRoleConflict(self, subject, obj, role):
        conflictingQueries = []

        # Sibling-like roles: subject should NOT be a parent of obj
        if role in ["sister", "brother", "uncle", "aunt"]:
            conflictingQueries += [
                f"parent({subject}, {obj})",
                f"mother({subject}, {obj})",
                f"father({subject}, {obj})"
            ]

        # Parent-like roles: subject should NOT be a sibling or child of obj
        elif role in ["mother", "father"]:
            conflictingQueries += [
                f"sibling({subject}, {obj})",
                f"parent({obj}, {subject})"
            ]

        # Grandparent roles: subject should NOT be a child or sibling of obj
        elif role in ["grandmother", "grandfather"]:
            conflictingQueries += [
                f"parent({obj}, {subject})",
                f"sibling({subject}, {obj})"
            ]

        # Sibling role (if using "sibling" directly, not sister/brother)
        elif role == "sibling":
            conflictingQueries += [
                f"parent({subject}, {obj})",
                f"parent({obj}, {subject})"
            ]

        # Query each potential conflict
        for query in conflictingQueries:
            try:
                results = list(self.prolog.query(query))
                if results:
                    return True  # Conflict found
            except Exception:
                continue  # Ignore failed queries

        return False  # No conflicts detected

    def learnFact(self, sentence: str):
        tokens = self.commandTokenizer(sentence)
        # print("DEBUG Tokens:", tokens)

        # <> and <> are siblings.
        if len(tokens) == 5 and tokens[1] == "and" and tokens[3] == "are" and tokens[
            4] == "siblings" and self.isValidName(tokens[0]) and self.isValidName(tokens[2]):
            sibling1 = tokens[0].lower()
            sibling2 = tokens[2].lower()

            if sibling1 == sibling2:
                self.printResponse(self.impossibleMessage)
                return

            results = list(
                self.prolog.query(f"parent(P, {sibling1}), parent(P, {sibling2}), {sibling1} \\= {sibling2}"))

            if results:
                self.printResponse(self.learnedSomethingMessage, "confirmed to be siblings")
            else:
                self.printResponse(self.impossibleMessage, "no shared parent yet")

        # <> is a brother of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "brother" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            brother = tokens[0].lower()
            sibling = tokens[5].lower()

            if brother == sibling:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(brother, sibling, "brother"):
                self.printResponse(self.impossibleMessage, "brother and sibling have role conflict")
            elif list(self.prolog.query(f"female({brother})")):
                self.printResponse(self.impossibleMessage, "brother can't be a female")
            elif not self.haveSharedParent(brother, sibling):
                self.printResponse(self.impossibleMessage, "brother and sibling have no shared parent")
            else:
                try:
                    self.prolog.assertz(f"male({brother})")
                    self.printResponse(self.learnedSomethingMessage, "confirmed brother")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

        # <> is a sister of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "sister" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            sister = tokens[0].lower()
            sibling = tokens[5].lower()

            if sister == sibling:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(sister, sibling, "sister"):
                self.printResponse(self.impossibleMessage, "sister and sibling have role conflict")
            elif list(self.prolog.query(f"male({sister})")):
                self.printResponse(self.impossibleMessage, "sister can't be a male")
            elif not self.haveSharedParent(sister, sibling):
                self.printResponse(self.impossibleMessage, "sister and sibling have no shared parent")
            else:
                try:
                    self.prolog.assertz(f"female({sister})")
                    self.printResponse(self.learnedSomethingMessage, "confirmed sister")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

        # <> is the father of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "the" and tokens[3] == "father" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            father = tokens[0].lower()
            child = tokens[5].lower()

            if father == child:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(father, child, "father"):
                self.printResponse(self.impossibleMessage, "child and father have role conflict")
                return

            if list(self.prolog.query(f"female({father})")):
                self.printResponse(self.impossibleMessage, "father can't be a female")
                return

            if list(self.prolog.query(f"ancestor({child}, {father})")):
                self.printResponse(self.impossibleMessage,
                                   f"{child.capitalize()} is already an ancestor of {father.capitalize()}.")
                return

            existing_father = list(self.prolog.query(f"father(F, {child})"))
            is_parent = bool(list(self.prolog.query(f"parent({father}, {child})")))
            is_mother = bool(list(self.prolog.query(f"mother({father}, {child})")))
            is_father = bool(list(self.prolog.query(f"father({father}, {child})")))
            n_parents = len(list(self.prolog.query(f"parent(P, {child})")))

            if n_parents == 0:
                try:
                    self.prolog.assertz(f"male({father})")
                    self.prolog.assertz(f"parent({father}, {child})")
                    self.printResponse(self.learnedSomethingMessage, "no parent initial: confirmed father")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)
                return

            elif n_parents == 1:
                if is_parent and not is_mother and not is_father:
                    try:
                        self.prolog.assertz(f"male({father})")
                        self.printResponse(self.learnedSomethingMessage,
                                           "1st parent initial: genderless - confirmed father")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    return
                elif existing_father:
                    if existing_father[0]["F"].lower() == father.lower():
                        existing = existing_father[0]["F"]
                        self.printResponse(self.learnedSomethingMessage,
                                           f"{existing.capitalize()} already has been a confirmed father of {child.capitalize()}")
                        return
                    else:
                        existing = existing_father[0]["F"]
                        self.printResponse(self.impossibleMessage,
                                           f"{child.capitalize()} already has a confirmed father: {existing.capitalize()}")
                        return
                else:
                    try:
                        self.prolog.assertz(f"male({father})")
                        self.prolog.assertz(f"parent({father}, {child})")
                        self.printResponse(self.learnedSomethingMessage, "1st parent mother: confirmed father")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    return

            else:
                self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has two known parents.")
                return

        # <> is the mother of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "the" and tokens[3] == "mother" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            mother = tokens[0].lower()
            child = tokens[5].lower()

            if mother == child:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(mother, child, "mother"):
                self.printResponse(self.impossibleMessage, "child and mother have role conflict")
                return

            if list(self.prolog.query(f"male({mother})")):
                self.printResponse(self.impossibleMessage, "mother can't be a male")
                return

            if list(self.prolog.query(f"ancestor({child}, {mother})")):
                self.printResponse(self.impossibleMessage,
                                   f"{child.capitalize()} is already an ancestor of {mother.capitalize()}.")
                return

            existing_mother = list(self.prolog.query(f"mother(M, {child})"))
            is_parent = bool(list(self.prolog.query(f"parent({mother}, {child})")))
            is_mother = bool(list(self.prolog.query(f"mother({mother}, {child})")))
            is_father = bool(list(self.prolog.query(f"father({mother}, {child})")))
            n_parents = len(list(self.prolog.query(f"parent(P, {child})")))

            if n_parents == 0:
                try:
                    self.prolog.assertz(f"female({mother})")
                    self.prolog.assertz(f"parent({mother}, {child})")
                    self.printResponse(self.learnedSomethingMessage, "no parent initial: confirmed mother")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)
                return

            elif n_parents == 1:
                if is_parent and not is_father and not is_mother:
                    try:
                        self.prolog.assertz(f"female({mother})")
                        self.printResponse(self.learnedSomethingMessage,
                                           "1st parent initial: genderless - confirmed mother")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    return
                elif existing_mother:
                    if existing_mother[0]["M"].lower() == mother.lower():
                        existing = existing_mother[0]["M"]
                        self.printResponse(self.learnedSomethingMessage,
                                           f"{existing.capitalize()} already has been a confirmed mother of {child.capitalize()}")
                        return
                    else:
                        existing = existing_mother[0]["M"]
                        self.printResponse(self.impossibleMessage,
                                           f"{child.capitalize()} already has a confirmed mother: {existing.capitalize()}")
                        return
                else:
                    try:
                        self.prolog.assertz(f"female({mother})")
                        self.prolog.assertz(f"parent({mother}, {child})")
                        self.printResponse(self.learnedSomethingMessage, "1st parent father: confirmed mother")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    return

            else:
                self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has two known parents.")
                return

        # <>, <> and <> are children of <>.
        elif len(tokens) == 8 and tokens[2] == "and" and tokens[4] == "are" and tokens[5] == "children" and tokens[
            6] == "of" and self.isValidName(tokens[0].strip(",")) and self.isValidName(tokens[1]) and self.isValidName(
            tokens[3]) and self.isValidName(tokens[7]):
            child1 = tokens[0].strip(",").lower()
            child2 = tokens[1].lower()
            child3 = tokens[3].lower()
            parent = tokens[7].lower()

            if len({child1, child2, child3, parent}) < 4:
                self.printResponse(self.impossibleMessage)
                return

            # ✅ Require known gender
            is_male = bool(list(self.prolog.query(f"male({parent})")))
            is_female = bool(list(self.prolog.query(f"female({parent})")))
            if not is_male and not is_female:
                self.printResponse(self.impossibleMessage,
                                   f"I need to know if {parent.capitalize()} is male or female first!")
                return

            # ✅ Prevent circular relationship
            for c in [child1, child2, child3]:
                if list(self.prolog.query(f"descendant({parent}, {c})")):
                    self.printResponse(self.impossibleMessage,
                                       f"{parent.capitalize()} is already a descendant of {c.capitalize()}.")
                    return

            for child in [child1, child2, child3]:
                existing_parents = list(self.prolog.query(f"parent(P, {child})"))

                if any(p["P"] == parent for p in existing_parents):
                    if self.debugMode:
                        self.printResponse(f"A-DBot > ⚠️ {child.capitalize()} already has {parent.capitalize()} as a parent.")
                    continue

                if len(existing_parents) >= 2:
                    self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has two known parents.")
                    return

                if len(existing_parents) == 1:
                    existing_parent = existing_parents[0]["P"]
                    if existing_parent != parent:
                        is_ep_male = bool(list(self.prolog.query(f"male({existing_parent})")))
                        is_ep_female = bool(list(self.prolog.query(f"female({existing_parent})")))

                        if is_male and is_ep_male:
                            self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has a male parent.")
                            return
                        elif is_female and is_ep_female:
                            self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has a female parent.")
                            return

            # ✅ Only assert for children that passed all checks
            try:
                for child in [child1, child2, child3]:
                    # Avoid asserting again if already known
                    already_known = list(self.prolog.query(f"parent({parent}, {child})"))
                    if not already_known:
                        self.prolog.assertz(f"parent({parent}, {child})")
                self.printResponse(self.learnedSomethingMessage, "all children confirmed")
            except Exception as e:
                self.printResponse(self.impossibleMessage)


        # <> and <> are the parents of <>.
        elif len(tokens) == 8 and tokens[1] == "and" and tokens[3] == "are" and tokens[4] == "the" and tokens[
            5] == "parents" and tokens[6] == "of" and self.isValidName(tokens[0]) and self.isValidName(
            tokens[2]) and self.isValidName(tokens[7]):
            parent1 = tokens[0].lower()
            parent2 = tokens[2].lower()
            child = tokens[7].lower()

            if parent1 == parent2 or parent1 == child or parent2 == child:
                self.printResponse(self.impossibleMessage)
                return

            # Check role conflicts first
            if self.hasRoleConflict(parent1, child, "father") or self.hasRoleConflict(parent2, child,
                                                                                      "mother") or self.hasRoleConflict(
                parent2, child, "father") or self.hasRoleConflict(parent1, child, "mother"):
                self.printResponse(self.impossibleMessage, "parents and child conflict")
                return

            # Check existing confirmed parents
            confirmed_father = list(self.prolog.query(f"father(F, {child})"))
            confirmed_mother = list(self.prolog.query(f"mother(M, {child})"))

            confirmed_parents = set()
            if confirmed_father:
                confirmed_parents.add(confirmed_father[0]["F"].lower())
            if confirmed_mother:
                confirmed_parents.add(confirmed_mother[0]["M"].lower())

            input_set = {parent1, parent2}

            if len(confirmed_parents) == 2:
                # Child already has 2 confirmed parents
                if confirmed_parents == input_set:
                    self.printResponse(self.learnedSomethingMessage,
                                       f"{child.capitalize()} already has these 2 as the confirmed parents")
                    return
                else:
                    self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has two confirmed parents.")
                    return

            if len(confirmed_parents) == 1:
                # One parent is confirmed — make sure they are part of the input
                if not confirmed_parents.issubset(input_set):
                    existing = next(iter(confirmed_parents))
                    self.printResponse(self.impossibleMessage,
                                       f"{child.capitalize()} already has a confirmed parent: {existing.capitalize()}")
                    return

                # Determine which one is confirmed and check the other’s gender
                other = (input_set - confirmed_parents).pop()
                if confirmed_father:
                    # Other must be mother
                    is_mother = list(self.prolog.query(f"female({other})"))
                    if not is_mother:
                        self.printResponse(self.impossibleMessage,
                                           f"{other.capitalize()} must be the mother, but I don't know or it's incorrect.")
                        return
                elif confirmed_mother:
                    # Other must be father
                    is_father = list(self.prolog.query(f"male({other})"))
                    if not is_father:
                        self.printResponse(self.impossibleMessage,
                                           f"{other.capitalize()} must be the father, but I don't know or it's incorrect.")
                        return

            if len(confirmed_parents) == 0:
                # No confirmed parents, so enforce gender check between inputs
                is_male_1 = list(self.prolog.query(f"male({parent1})"))
                is_female_1 = list(self.prolog.query(f"female({parent1})"))
                is_male_2 = list(self.prolog.query(f"male({parent2})"))
                is_female_2 = list(self.prolog.query(f"female({parent2})"))

                if (is_male_1 and is_female_2) or (is_male_2 and is_female_1):
                    pass  # OK
                else:
                    self.printResponse(self.impossibleMessage, f"Cannot confirm opposite-gender roles for parents.")
                    return

            # Passed all checks
            try:
                self.prolog.assertz(f"parent({parent1}, {child})")
                self.prolog.assertz(f"parent({parent2}, {child})")
                self.printResponse(self.learnedSomethingMessage, "both parents of child confirmed ")
            except Exception as e:
                self.printResponse(self.impossibleMessage)

        # <> is a child of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "child" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            child = tokens[0].lower()
            parent = tokens[5].lower()

            if child == parent:
                self.printResponse(self.impossibleMessage)
                return

            # ✅ Require known gender
            is_male = bool(list(self.prolog.query(f"male({parent})")))
            is_female = bool(list(self.prolog.query(f"female({parent})")))
            if not is_male and not is_female:
                self.printResponse(self.impossibleMessage,
                                   f"I need to know if {parent.capitalize()} is male or female first!")
                return

            if list(self.prolog.query(f"descendant({parent}, {child})")):
                self.printResponse(self.impossibleMessage,
                                   f"That would create a cycle: {parent.capitalize()} is already a descendant of {child.capitalize()}.")
                return

            existing_parents = list(self.prolog.query(f"parent(P, {child})"))

            if len(existing_parents) >= 2:
                self.printResponse(self.impossibleMessage,
                                   f"{child.capitalize()} already has two known parents.")
                return

            if len(existing_parents) == 1:
                existing_parent = existing_parents[0]["P"]
                if existing_parent == parent:
                    if self.debugMode:
                        self.printResponse(f"A-DBot > ⚠️ {child.capitalize()} already has {parent.capitalize()} as a parent.")
                # Get gender of existing parent
                is_ep_male = bool(list(self.prolog.query(f"male({existing_parent})")))
                is_ep_female = bool(list(self.prolog.query(f"female({existing_parent})")))

                if is_male and is_ep_male:
                    self.printResponse(self.impossibleMessage,
                                       f"{child.capitalize()} already has a male parent.")
                    return
                elif is_female and is_ep_female:
                    self.printResponse(self.impossibleMessage,
                                       f"{child.capitalize()} already has a female parent.")
                    return
            try:
                self.prolog.assertz(f"parent({parent}, {child})")
                self.printResponse(self.learnedSomethingMessage, "confirmed child of parent")
            except Exception as e:
                self.printResponse(self.impossibleMessage)

        # <> is a grandmother of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "grandmother" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            subject = tokens[0].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(subject, obj, "grandmother"):
                self.printResponse(self.impossibleMessage,
                                   f"grandmother and grandchild role conflict")
                return
            elif list(self.prolog.query(f"male({subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"grandmother can't be male")
                return
            else:
                try:
                    query = f"parent({subject}, M), parent(M, {obj})"
                    if list(self.prolog.query(query)):
                        self.prolog.assertz(f"female({subject})")
                        self.printResponse(self.learnedSomethingMessage, "Got it! The grandmother relationship is now logically true.")
                    else:
                        self.printResponse(self.impossibleMessage, "Cannot learn that yet: no supporting parent-child relationships.")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

        # <> is a grandfather of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "grandfather" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            subject = tokens[0].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(subject, obj, "grandfather"):
                self.printResponse(self.impossibleMessage,
                                   f"grandfather and grandchild role conflict")
                return
            elif list(self.prolog.query(f"female({subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"grandfather can't be female")
                return
            else:
                try:
                    query = f"parent({subject}, M), parent(M, {obj})"
                    if list(self.prolog.query(query)):
                        self.prolog.assertz(f"male({subject})")
                        self.printResponse(self.learnedSomethingMessage, "Got it! The grandfather relationship is now logically true.")
                    else:
                        self.printResponse(self.impossibleMessage, "Cannot learn that yet: no supporting parent-child relationships.")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

        # <> is a daughter of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "daughter" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            subject = tokens[0].lower()
            parent = tokens[5].lower()

            if subject == parent:
                self.printResponse(self.impossibleMessage)
                return

            if list(self.prolog.query(f"descendant({parent}, {subject})")):
                self.printResponse(self.impossibleMessage, f"{parent.capitalize()} is already a descendant of {subject.capitalize()}.")
                return

            if list(self.prolog.query(f"male({subject})")):
                self.printResponse(self.impossibleMessage, "daughter can't be male")
                return

            # Get all the children of X
            children = list(self.prolog.query(f"parent({subject}, C)"))

            for c in children:
                child = c["C"]

                # Check if the child already has a confirmed mother
                confirmed_mother = list(self.prolog.query(f"mother(M, {child})"))

                if confirmed_mother and confirmed_mother[0]["M"].lower() != subject.lower():
                    self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has a different confirmed mother: {confirmed_mother[0]['M'].capitalize()}")
                    return

            # Check existing parent (either mother or father)
            existing_mother = list(self.prolog.query(f"mother(M, {subject})"))
            existing_father = list(self.prolog.query(f"father(F, {subject})"))
            parents = list(self.prolog.query(f"parent(P, {subject})"))
            n_parents = len(list(self.prolog.query(f"parent(P, {subject})")))

            if n_parents == 0:
                try:
                    self.prolog.assertz(f"female({subject})")
                    self.prolog.assertz(f"parent({parent}, {subject})")
                    self.printResponse(self.learnedSomethingMessage, f"0 parent - confirmed daughter of parent")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

            elif n_parents == 1:
                if existing_father or existing_mother:

                    # ❌ Case: Has one parent, and new parent has unknown gender
                    gender_known = list(self.prolog.query(f"male({parent})")) or list(
                        self.prolog.query(f"female({parent})"))
                    if not gender_known and (existing_mother or existing_father):
                        self.printResponse(self.impossibleMessage,
                                           f"1 parent - {subject.capitalize()} already has a confirmed parent. I can't assign an unknown-gender parent.")
                        return

                    isMale = bool(list(self.prolog.query(f"male({parent})")))
                    isFemale = bool(list(self.prolog.query(f"female({parent})")))

                    if existing_mother:
                        known = existing_mother[0]["M"]
                        if known != parent and isMale:
                            try:
                                self.prolog.assertz(f"female({subject})")
                                self.prolog.assertz(f"parent({parent}, {subject})")
                                self.printResponse(self.learnedSomethingMessage,
                                                   f"1 parent - {subject.capitalize()} already has a confirmed mother: {known.capitalize()}")
                            except Exception as e:
                                self.printResponse(self.impossibleMessage)
                        elif known == parent and isFemale:
                            self.prolog.assertz(f"female({subject})")
                            self.printResponse(self.learnedSomethingMessage,
                                                   f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                        else:
                            self.printResponse(self.impossibleMessage,
                                                   f"{subject.capitalize()} already has a mother ({known.capitalize()})")

                    # ✅ Case: Reaffirm known father
                    if existing_father:
                        known = existing_father[0]["F"]
                        if known != parent and isFemale:
                            try:
                                self.prolog.assertz(f"female({subject})")
                                self.prolog.assertz(f"parent({parent}, {subject})")
                                self.printResponse(self.learnedSomethingMessage,
                                                   f"1 parent - {subject.capitalize()} already has a confirmed father: {known.capitalize()}")
                            except Exception as e:
                                self.printResponse(self.impossibleMessage)
                        elif known == parent and isMale:
                            self.prolog.assertz(f"female({subject})")
                            self.printResponse(self.learnedSomethingMessage,
                                                   f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                        else:
                            self.printResponse(self.impossibleMessage,
                                                   f"{subject.capitalize()} already has a father ({known.capitalize()})")
                else:
                    self.prolog.assertz(f"female({subject})")
                    known = parents[0]["P"]
                    if known == parent:
                        self.printResponse(self.learnedSomethingMessage, f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                    else:
                        self.printResponse(self.impossibleMessage, "has a parent but genderless please declare the first parent's gender first")
            elif n_parents >= 2:
                # ✅ Bypass: allow reasserting an already-known parent
                if (existing_father and existing_father[0]["F"] == parent) or \
                        (existing_mother and existing_mother[0]["M"] == parent):
                    try:
                        self.prolog.assertz(f"female({subject})")
                        self.printResponse(self.learnedSomethingMessage,
                                           f"2 parents - confirmed daughter of parents")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    pass  # reasserting same parent is OK
                else:
                    self.printResponse(self.impossibleMessage, f"{subject.capitalize()} already has two known parents.")
                    return

        # <> is a son of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "a" and tokens[3] == "son" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            subject = tokens[0].lower()
            parent = tokens[5].lower()

            if subject == parent:
                self.printResponse(self.impossibleMessage)
                return

            if list(self.prolog.query(f"descendant({parent}, {subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"{parent.capitalize()} is already a descendant of {subject.capitalize()}.")
                return

            # ❌ Contradiction with known gender
            if list(self.prolog.query(f"female({subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"son can't be female")
                return

            children = list(self.prolog.query(f"parent({subject}, C)"))

            for c in children:
                child = c["C"]

                # Check if the child already has a confirmed father
                confirmed_father = list(self.prolog.query(f"father(F, {child})"))

                if confirmed_father and confirmed_father[0]["F"].lower() != subject.lower():
                    self.printResponse(self.impossibleMessage, f"{child.capitalize()} already has a different confirmed father: {confirmed_father[0]['F'].capitalize()}")
                    return

            existing_mother = list(self.prolog.query(f"mother(M, {subject})"))
            existing_father = list(self.prolog.query(f"father(F, {subject})"))
            parents = list(self.prolog.query(f"parent(P, {subject})"))
            n_parents = len(list(self.prolog.query(f"parent(P, {subject})")))

            if n_parents == 0:
                try:
                    self.prolog.assertz(f"male({subject})")
                    self.prolog.assertz(f"parent({parent}, {subject})")
                    self.printResponse(self.learnedSomethingMessage, f"0 parent - confirmed son of parent")
                except Exception as e:
                    self.printResponse(self.impossibleMessage)

            elif n_parents == 1:
                if existing_father or existing_mother:

                    # ❌ Case: Has one parent, and new parent has unknown gender
                    gender_known = list(self.prolog.query(f"male({parent})")) or list(
                        self.prolog.query(f"female({parent})"))
                    if not gender_known and (existing_mother or existing_father):
                        self.printResponse(self.impossibleMessage, f"1 parent - {subject.capitalize()} already has a confirmed parent. I can't assign an unknown-gender parent.")
                        return

                    isMale = bool(list(self.prolog.query(f"male({parent})")))
                    isFemale = bool(list(self.prolog.query(f"female({parent})")))

                    if existing_mother:
                        known = existing_mother[0]["M"]
                        if known != parent and isMale:
                            try:
                                self.prolog.assertz(f"male({subject})")
                                self.prolog.assertz(f"parent({parent}, {subject})")
                                self.printResponse(self.learnedSomethingMessage,
                                                   f"1 parent - {subject.capitalize()} already has a confirmed mother: {known.capitalize()}")
                            except Exception as e:
                                self.printResponse(self.impossibleMessage)
                        elif known == parent and isFemale:
                            self.prolog.assertz(f"male({subject})")
                            self.printResponse(self.learnedSomethingMessage,
                                               f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                        else:
                            self.printResponse(self.impossibleMessage,
                                               f"{subject.capitalize()} already has a mother ({known.capitalize()})")

                    # ✅ Case: Reaffirm known father
                    if existing_father:
                        known = existing_father[0]["F"]
                        if known != parent and isFemale:
                            try:
                                self.prolog.assertz(f"male({subject})")
                                self.prolog.assertz(f"parent({parent}, {subject})")
                                self.printResponse(self.learnedSomethingMessage, f"1 parent - {subject.capitalize()} already has a confirmed father: {known.capitalize()}")
                            except Exception as e:
                                self.printResponse(self.impossibleMessage)
                        elif known == parent and isMale:
                            self.prolog.assertz(f"male({subject})")
                            self.printResponse(self.learnedSomethingMessage,
                                               f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                        else:
                            self.printResponse(self.impossibleMessage, f"{subject.capitalize()} already has a father ({known.capitalize()})")
                else:
                    self.prolog.assertz(f"male({subject})")
                    known = parents[0]["P"]
                    if known == parent:
                        self.printResponse(self.learnedSomethingMessage,
                                           f"already knew {parent.capitalize()} is the parent of {subject.capitalize()}")
                    else:
                        self.printResponse(self.impossibleMessage, "has a parent but genderless please declare the first parent's gender first")

            # ❌ Case: Already has two parents
            elif n_parents >= 2:
                # ✅ Bypass: allow reasserting an already-known parent
                if (existing_father and existing_father[0]["F"] == parent) or \
                        (existing_mother and existing_mother[0]["M"] == parent):
                    try:
                        self.prolog.assertz(f"male({subject})")
                        self.printResponse(self.learnedSomethingMessage,
                                           f"2 parents - confirmed daughter of parents")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                    pass  # reasserting same parent is OK
                else:
                    self.printResponse(self.impossibleMessage, f"{subject.capitalize()} already has two known parents.")
                    return

        # <> is an uncle of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "an" and tokens[3] == "uncle" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):

            subject = tokens[0].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(subject, obj, "uncle"):
                self.printResponse(self.impossibleMessage, "pamangkin uncle role conflict")
                return

            if list(self.prolog.query(f"female({subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"uncle can't be female")
                return

            else:
                # Check if subject is brother of a parent of obj
                query = f"sibling({subject}, X), parent(X, {obj})"
                if list(self.prolog.query(query)):
                    try:
                        self.prolog.assertz(f"male({subject})")  # Only assert male, uncle is deduced
                        self.printResponse(self.learnedSomethingMessage, "pamangkin uncle relationship confirmed.")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                else:
                    self.printResponse(self.impossibleMessage, "pamangkin uncle relationship not confirmed.")

        # <> is an aunt of <>.
        elif len(tokens) == 6 and tokens[1] == "is" and tokens[2] == "an" and tokens[3] == "aunt" and tokens[
            4] == "of" and self.isValidName(tokens[0]) and self.isValidName(tokens[5]):
            subject = tokens[0].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse(self.impossibleMessage)
                return

            if self.hasRoleConflict(subject, obj, "aunt"):
                self.printResponse(self.impossibleMessage, "pamangkin aunt role conflict")
                return

            if list(self.prolog.query(f"male({subject})")):
                self.printResponse(self.impossibleMessage,
                                   f"aunt can't be a male")
                return

            else:
                query = f"sibling({subject}, X), parent(X, {obj})"
                if list(self.prolog.query(query)):
                    try:
                        self.prolog.assertz(f"female({subject})")  # Only assert female
                        self.printResponse(self.learnedSomethingMessage, "pamangkin aunt relationship confirmed.")
                    except Exception as e:
                        self.printResponse(self.impossibleMessage)
                else:
                    self.printResponse(self.impossibleMessage, "pamangkin aunt relationship not confirmed.")
        else:
            self.printResponse("A-DBot > Invalid statement format.")

    def answerQuestion(self, question: str):
        tokens = self.commandTokenizer(question)
        # print("DEBUG Tokens:", tokens)

        # Are <> and <> siblings?
        if len(tokens) == 5 and tokens[0] == "Are" and tokens[2] == "and" and tokens[
            4] == "siblings" and self.isValidName(tokens[1]) and self.isValidName(tokens[3]):
            name1 = tokens[1].lower()
            name2 = tokens[3].lower()

            if name1 == name2:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"sibling({name1}, {name2})"))
            if results:
                self.printResponse2("Yes!", "Yes, they are siblings.")
            else:
                self.printResponse2("No.", "No, they are not siblings.")

        # Is <> a sister of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "sister" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"sister({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, she is a sister.")
            else:
                self.printResponse2("No.", "No, she is not a sister.")

        # Is <> a brother of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "brother" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"brother({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, he is a brother.")
            else:
                self.printResponse2("No.", "No, he is not a brother.")

        # Is <> the mother of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "the" and tokens[3] == "mother" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"mother({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, she is the mother.")
            else:
                self.printResponse2("No.", "No, she is not the mother.")

        # Is <> the father of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "the" and tokens[3] == "father" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"father({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, he is the father.")
            else:
                self.printResponse2("No.", "No, he is not the father.")

        # Are <> and <> the parents of <>?
        elif len(tokens) == 8 and tokens[0] == "Are" and tokens[2] == "and" and tokens[4] == "the" and tokens[
            5] == "parents" and tokens[6] == "of" and self.isValidName(tokens[1]) and self.isValidName(
            tokens[3]) and self.isValidName(tokens[7]):
            name1 = tokens[1].lower()
            name2 = tokens[3].lower()
            child = tokens[7].lower()

            if len({name1, name2, child}) < 3:
                self.printResponse2("No.")
                return

            results1 = list(self.prolog.query(f"parent({name1}, {child})"))
            results2 = list(self.prolog.query(f"parent({name2}, {child})"))
            if results1 and results2:
                self.printResponse2("Yes!", "Yes, both are the parents.")
            else:
                self.printResponse2("No.", "No, both are not confirmed as parents.")

        # Is <> a grandmother of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "grandmother" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"grandmother({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, she is the grandmother.")
            else:
                self.printResponse2("No.", "No, she is not the grandmother.")

        # Is <> a grandfather of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "grandfather" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"grandfather({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, he is the grandfather.")
            else:
                self.printResponse2("No.", "No, he is not the grandfather.")

        # Is <> a daughter of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "daughter" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"daughter({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, she is the daughter.")
            else:
                self.printResponse2("No.", "No, she is not the daughter.")

        # Is <> a son of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "son" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"son({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, he is the son.")
            else:
                self.printResponse2("No.", "No, he is not the son.")

        # Is <> a child of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "a" and tokens[3] == "child" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"child({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, that is their child.")
            else:
                self.printResponse2("No.", "No, not a child of that person.")

        # Are <>, <> and <> children of <>?
        elif len(tokens) == 8 and tokens[0] == "Are" and tokens[3] == "and" and tokens[5] == "children" and tokens[
            6] == "of" and self.isValidName(tokens[1].strip(",")) and self.isValidName(tokens[2]) and self.isValidName(
            tokens[4]) and self.isValidName(tokens[7]):
            child1 = tokens[1].strip(",").lower()
            child2 = tokens[2].lower()
            child3 = tokens[4].lower()
            parent = tokens[7].lower()

            if len({child1, child2, child3, parent}) < 4:
                self.printResponse2("No.")
                return

            results1 = list(self.prolog.query(f"parent({parent}, {child1})"))
            results2 = list(self.prolog.query(f"parent({parent}, {child2})"))
            results3 = list(self.prolog.query(f"parent({parent}, {child3})"))

            if results1 and results2 and results3:
                self.printResponse2("Yes!", "Yes, all are children of that parent.")
            else:
                self.printResponse2("No.", "No, not all are children of that parent.")

        # Is <> an aunt of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "an" and tokens[3] == "aunt" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"aunt({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, she is the aunt.")
            else:
                self.printResponse2("No.", "No, she is not the aunt.")

        # Is <> an uncle of <>?
        elif len(tokens) == 6 and tokens[0] == "Is" and tokens[2] == "an" and tokens[3] == "uncle" and tokens[
            4] == "of" and self.isValidName(tokens[1]) and self.isValidName(tokens[5]):
            subject = tokens[1].lower()
            obj = tokens[5].lower()

            if subject == obj:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"uncle({subject}, {obj})"))
            if results:
                self.printResponse2("Yes!", "Yes, he is the uncle.")
            else:
                self.printResponse2("No.", "No, he is not the uncle.")

        # Are <> and <> relatives?
        elif len(tokens) == 5 and tokens[0] == "Are" and tokens[2] == "and" and tokens[
            4] == "relatives" and self.isValidName(tokens[1]) and self.isValidName(tokens[3]):
            name1 = tokens[1].lower()
            name2 = tokens[3].lower()

            if name1 == name2:
                self.printResponse2("No.")
                return

            results = list(self.prolog.query(f"relative({name1}, {name2})"))
            if results:
                self.printResponse2("Yes!", "Yes, they are relatives.")
            else:
                self.printResponse2("No.", "No, they are not relatives.")

        # Who are the siblings of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "siblings"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"sibling(X, {subject})"))
            if results:
                siblings = sorted(set(result["X"] for result in results))
                self.printResponse2(
                    f"{', '.join(name.capitalize() for name in siblings)}")
            else:
                self.printResponse2(f"No known siblings for {subject.capitalize()}.")

        # Who are the sisters of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "sisters"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"sister(X, {subject})"))
            if results:
                sisters = sorted(set(result["X"] for result in results))
                self.printResponse2(
                    f"{', '.join(name.capitalize() for name in sisters)}")
            else:
                self.printResponse2(f"No known sisters for {subject.capitalize()}.")

        # Who are the brothers of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "brothers"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"brother(X, {subject})"))
            if results:
                brothers = sorted(set(result["X"] for result in results))
                self.printResponse2(
                    f"{', '.join(name.capitalize() for name in brothers)}")
            else:
                self.printResponse2(f"No known brothers for {subject.capitalize()}.")

        # Who is the mother of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "is", "the", "mother"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"mother(X, {subject})"))
            if results:
                mothers = sorted(set(result["X"] for result in results))
                self.printResponse2(
                    f"{', '.join(name.capitalize() for name in mothers)}")
            else:
                self.printResponse2(f"No known mother for {subject.capitalize()}.")

        # Who is the father of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "is", "the", "father"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"father(X, {subject})"))
            if results:
                fathers = sorted(set(str(result["X"]).capitalize() for result in results))
                self.printResponse2(f"{', '.join(fathers)}")
            else:
                self.printResponse2(f"No known father for {subject.capitalize()}.")

        # Who are the parents of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "parents"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"parent(X, {subject})"))
            if results:
                parents = sorted(set(str(result["X"]).capitalize() for result in results))
                self.printResponse2(f"{', '.join(parents)}")
            else:
                self.printResponse2(f"No known parents for {subject.capitalize()}.")

        # Who are the daughters of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "daughters"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"daughter(X, {subject})"))
            if results:
                daughters = sorted(set(str(result["X"]).capitalize() for result in results))
                self.printResponse2(f"{', '.join(daughters)}")
            else:
                self.printResponse2(f"No known daughters for {subject.capitalize()}.")

        # Who are the sons of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "sons"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"son(X, {subject})"))
            if results:
                sons = sorted(set(str(result["X"]).capitalize() for result in results))
                self.printResponse2(f"{', '.join(sons)}")
            else:
                self.printResponse2(f"No known sons for {subject.capitalize()}.")

        # Who are the children of <>?
        elif len(tokens) == 6 and tokens[:4] == ["Who", "are", "the", "children"] and self.isValidName(tokens[5]):
            subject = tokens[5].lower()
            results = list(self.prolog.query(f"child(X, {subject})"))
            if results:
                children = sorted(set(str(result["X"]).capitalize() for result in results))
                self.printResponse2(f"{', '.join(children)}")
            else:
                self.printResponse2(f"No known children for {subject.capitalize()}.")
        else:
            self.printResponse2("Invalid question format.")


if __name__ == "__main__":
    bot = ADBot()

    while True:
        try:
            userInput = input("\n  You  > ").strip()
            if userInput.lower() in {"exit", "quit"}:
                bot.printResponse2("A-DBot signing off. Goodbye!")
                break
            elif userInput.endswith("."):
                bot.learnFact(userInput)
            elif userInput.endswith("?"):
                bot.answerQuestion(userInput)
            else:
                bot.printResponse2("Please end your input with a period (.) for statements or a question mark (?) for questions.")
        except KeyboardInterrupt:
            print("")
            bot.printResponse2("A-DBot shutting down. See you!")
            break
