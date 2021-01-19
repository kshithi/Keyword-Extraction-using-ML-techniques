from collections import OrderedDict
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS

nlp = spacy.load('en_core_web_sm')


class txtrank():
    """Extract keywords from text"""

    def __init__(self):
        self.d = 0.85  # damping coefficient, usually is .85
        self.min_diff = 1e-5  # convergence threshold
        self.steps = 10  # iteration steps
        self.node_weight = None  # save keywords and its weight

    def set_stopwords(self, stopwords):
        """Set stop words"""
        for word in STOP_WORDS.union(set(stopwords)):
            lexeme = nlp.vocab[word]
            lexeme.is_stop = True

    def sentence_segment(self, doc, candidate_pos, lower):
        """Store those words only in cadidate_pos"""
        sentences = []
        for sent in doc.sents:
            selected_words = []
            for token in sent:
                # Store words only with cadidate POS tag
                if token.pos_ in candidate_pos and token.is_stop is False:
                    if lower is True:
                        selected_words.append(token.text.lower())
                    else:
                        selected_words.append(token.text)
            sentences.append(selected_words)
        return sentences

    def get_vocab(self, sentences):
        """Get all tokens"""
        vocab = OrderedDict()
        i = 0
        for sentence in sentences:
            for word in sentence:
                if word not in vocab:
                    vocab[word] = i
                    i += 1
        return vocab

    def get_token_pairs(self, window_size, sentences):
        """Build token_pairs from windows in sentences"""
        token_pairs = list()
        for sentence in sentences:
            for i, word in enumerate(sentence):
                for j in range(i + 1, i + window_size):
                    if j >= len(sentence):
                        break
                    pair = (word, sentence[j])
                    if pair not in token_pairs:
                        token_pairs.append(pair)
        return token_pairs

    def symmetrize(self, a):
        return a + a.T - np.diag(a.diagonal())

    def get_matrix(self, vocab, token_pairs):
        """Get normalized matrix"""
        # Build matrix
        vocab_size = len(vocab)
        g = np.zeros((vocab_size, vocab_size), dtype='float')
        for word1, word2 in token_pairs:
            i, j = vocab[word1], vocab[word2]
            g[i][j] = 1

        # Get Symmeric matrix
        g = self.symmetrize(g)

        # Normalize matrix by column
        norm = np.sum(g, axis=0)
        g_norm = np.divide(g, norm, where=norm != 0)  # this is ignore the 0 element in norm

        return g_norm

    def get_keywords(self, number=10):
        """Print top number keywords"""
        node_weight = OrderedDict(sorted(self.node_weight.items(), key=lambda t: t[1], reverse=True))
        for i, (key, value) in enumerate(node_weight.items()):
            print(key + ' - ' + str(value))
            if i > number:
                break

    def analyze(self, text,
                candidate_pos=['NOUN', 'PROPN'],
                window_size=4, lower=False, stopwords=list()):
        """Main function to analyze text"""

        # Set stop words
        self.set_stopwords(stopwords)

        # Pare text by spaCy
        doc = nlp(text)

        # Filter sentences
        sentences = self.sentence_segment(doc, candidate_pos, lower)  # list of list of words

        # Build vocabulary
        vocab = self.get_vocab(sentences)

        # Get token_pairs from windows
        token_pairs = self.get_token_pairs(window_size, sentences)

        # Get normalized matrix
        g = self.get_matrix(vocab, token_pairs)

        # Initionlization for weight(pagerank value)
        pr = np.array([1] * len(vocab))

        # Iteration
        previous_pr = 0
        for epoch in range(self.steps):
            pr = (1 - self.d) + self.d * np.dot(g, pr)
            if abs(previous_pr - sum(pr)) < self.min_diff:
                break
            else:
                previous_pr = sum(pr)

        # Get weight for each node
        node_weight = dict()
        for word, index in vocab.items():
            node_weight[word] = pr[index]

        self.node_weight = node_weight

text = '''The plaintiff filed this action for a declaration of title to premises No. 75, Sea Street, Galle, for ejectment of the defendant from the said premises and for damages at the rate of Rs. 30/- per month from 3.5.66 until restoration of possession.
 One Amaradasa had been the owner of the premises and Lucihamy was in occupation of it as his tenant. In April 1964, Amaradasa sold and conveyed the premises to the plaintiff for a consideration provided by A. M. N. Sideek, the father of the plaintiff. The plaintiff was at the time a student in the H.S.C. class.
 The plaintiff's case was that Mr. A. H. Jamaldeen, the Notary who attested the deed of conveyance in his favour wrote to Lucihamy informing her of the transfer by Amaradasa to the plaintiff: that Lucihamy came one day to Jamaldeen's office and plaintiff also came there and that Lucihamy agreed to accept the plaintiff as landlord and to pay rent to him. Rents were paid by Lucihamy in the shop of the plaintiff's father and receipts have been signed by the plaintiff's brother. The plaintiff further averred that Lucihamy died on the 3rd May, 1966 and the defendant, who is the daughter of Lucihamy, refused to vacate the premises and is in unlawful occupation of it.
187
The defendant's case was that after the transfer by Amaradasa to the Plaintiff, Amaradasa and A. M. M. Sideek came to the premises and Amaradasa indicated that rents should thereafter be paid to A. M. M. Sideek. Lucihamy paid rents at the shop of A. M. M. Sideek. The defendant further stated that when Lucihamy died she told A. M. M. Sideek that she would be paying the rent thereafter and that A. M. M. Sideek acquiesced and agreed but later put off accepting the rent. In January 1967, as Sideek refused to accept money, she deposited it with the Rent Control Board. After that she had regularly made deposits at the Rent Control Board up to May, 1969, In July, 1968 the defendant made an application to the Rent Control Board with regard to a latrine to the premises. At the inquiry at which she was unrepresented the lawyer appearing for A. M. M. Sideek produced the deed of transfer and stated that he was not the owner.
 On the question whether the landlord was A. M. M. Sideek, the plaintiff's father or the plaintiff, the learned District Judge states, "It is clear that the plaintiff has bought these premises in his name and if that was so, there was no reason why his father should be the landlord when ordinarily it is the owner who becomes the landlord. I, therefore, do not accept the position of the defendant when she said that she was the tenant of Sideek Mudalali." Later in his judgment, he said: - "It is difficult to believe that Lucihamy was the tenant of the father of the plaintiff." The learned district judge apparently thought it improbable that a person who buys property with his own money in the name of his son who is a H.S.C. student would let out the property himself. He found it difficult to believe that such a thing could happen. It appears to me that it is more probable that in such circumstances the father would let out the premises and act as landlord than that the H.S.C. student would do so. In point of fact the plaintiff admitted that his father looked after his property though he qualified it by saying that he did so when he was not there
 "Q: Sometimes your father also looked after the property?
 A: Yes, if I am not there. I had complete confidence in my father in the way he managed the property on my behalf."
 The rent was paid at the father's shop and receipts have been signed by the plaintiff's brother who was at the counter there. The plaintiff at that time must have been in the classroom doing his studies. In the counterfoil of one receipt (P7) dated 3.11.65, the words "for M. A. M. Sideek" appear below the signature. In an earlier receipt (DI) of 29th September, 1965, the counterfoil of which is the document P6, the frank of A. M. M. Sideek is placed on the stamp. The other receipts and counterfoil bear indecipherable signatures but the plaintiff's brother who gave evidence stated that it was his signature.
188
It appears to me that the learned District Judge's approach to the evidence is vitiated by the fact that he went on the basis that it was improbable and difficult to believe that plaintiff's father who had purchased the premises in the name of his student son with his own money was the landlord. This basis is in my opinion incorrect and erroneous. It appears to me that it is quite probable that A. M. M. Sideek was the landlord and that Lucihamy paid rents at his shop to him. The plaintiff stated in evidence, "Lucihamy died on 3.5.66. Thereafter the tenancy terminated on her death. The defendant occupied these premises forcibly". If this was in fact the position, it is difficult to understand why the plaintiff waited till November, 1968 to file action. From the 1st of January, 1967 the defendant was depositing rent with the Rent Control Board, and continued to be in occupation of the premises. On 11th July, 1968 she made the application to the Rent Control Board in respect of the latrine for these premises. The order of the Rent Control Board was made on the 13th August, 1968. It would appear that in September the plaintiff applied to the Conciliation Board with a view to filing action. He admitted in evidence that at the Conciliation Board he stated that he wanted the house for the purpose of effecting renovation. The plaintiff stated in evidence that he did not know that the defendant had made an application to the Rent Control Board and that at no time did his father tell him that he had to attend an inquiry at the Rent Control Board in connection with these premises.
 This last item of evidence is hardly credible on the footing that the plaintiff at all times was the landlord and acted as landlord. The evidence may however well be true and it suggests that it was the plaintiff's father who was dealing with all matters connected with the tenancy of these premises and he did not even care to keep his son informed of what occurred. The plaintiff did not even know that his list of documents included a certified copy of the application to the Rent Control Board. Even in regard to the conduct of this action, instructions appear to have been given by someone
10/31/2020 Ariyanandhi V. Mohamed Sideek
https://www.lawlanka.com/lal/pages/popUp/printNLRCaseReportPopUp.jsp?caseId=NLR80V186 2/4
other than the plaintiff and in the circumstances in all probability by the plaintiff's father. The learned District Judge had placed much reliance on the evidence of Mr. Jamaldeen who is a Proctor practising in his Court. It is not, however, possible to consider that Mr. Jamaldeen's evidence is without infirmities. He stated that he realised the significance of the letter he sent to Lucihamy and he sent it by registered post. Though he made a search he was unable to trace the registered postal article receipt. As he was not a civil practitioner, he did not maintain a separate book in which he made entries of registered letters sent by him. A carbon copy of the letters sent by him did not bear the word "registered" and he said it was not his practice to put the
189
word 'registered' on his letters. Finally, he said it may have been sent by express post. A question put to him and the answer given by him was as follows:
 Q: There is nothing to prove that this letter had been sent under registered post?
 A: As I was in a hurry I have on an oversight not made an entry. It is not necessary to write the word "registered". It is now five years and I could not trace the receipts. It may have been an express letter.
 He stated that the plaintiff is a nephew of his as he happened to be his younger sister-in-law's son. It appears to me that the learned District Judge has given too much weight to his evidence.
 For some reason which is not apparent, probably because of some difficulty of proof, the defendant was forced to call the plaintiff's father as a witness. Plaintiff's father was the alter ego of the plaintiff or it may even be more correctly stated that he was the principal actor and his son played a minor role.
 The learned District Judge, however, did not accept the evidence of the defendant because it was contrary to that of her own witness, the plaintiff's father. I do not think that this was a correct approach to the matter.
 I am of the view that it has been established on the probabilities that A. M. M. Sideek was the landlord and Lucihamy was his tenant at the time of her death.
 In the event of the death of a tenant, Section 18(2) of the Rent Restriction Act, Chapter 274 as amended by Act No. 10 of 1967 provides:
 "any person who
 (a) is the surviving spouse or the child, parent, brother or sister of the deceased tenant in premises, or was a dependent of the deceased tenant of the premises immediately prior to his death; and
 (b) was a member of the household of the deceased tenant (whether in those premises or in any other premises) during the whole of the period of three months preceding his death. 
 shall be entitled to give written notice to the landlord before expiry of two months after the last day of the month succeeding that in which the
190
death occurred to the effect, that he proposed to continue in occupation of the premises as tenant thereof and upon such written notice being given such person shall, subject to any order of the Board as hereinafter provided, be deemed for the purpose of the Act to be the tenant of the premises with effect from the 1st day of the month succeeding the month in which the death occurred, and the provisions of the Act shall apply accordingly". 
 Learned Counsel for the appellant submitted that the defendant was a person who was entitled to give notice in terms of this provision. In giving evidence the defendant stated, "I know the premises in suit. I have stayed in that house for 36 years". As however there was no express evidence as to whether she was a member of the household or not, Court gave the appellant an opportunity to submit documentary evidence with notice to counsel for the respondent. The defendant has submitted an affidavit to which is annexed certified copies of the householder's lists for the years 1964 and 1965 signed by Lucihamy and a certified copy of the householder's list for the year 1966 signed by her husband on 10th May, 1966 after the death of Lucihamy, in all of which the defendant's name appears as an occupant of these premises. There is also annexed a certificate from the Chairman of the Authorised Rice Ration Dealers Society, Galle, stating that he has supplied rice and other rations up to 1966 to Lucihamy and the defendant and the other occupants of these premises whose names are given on the householder's list and that from May, 1966 to 1973 he has supplied provisions to H. P. Piyadasa, the husband of the defendant, the defendant and their children. There also appears a certified extract from the electoral list for the years 1964, 1965 and 1966 in which the name of the defendant appears as living in these premises. It has, therefore, been established beyond doubt that the defendant is a person who was entitled under Section 18(2) to give notice to the landlord that she proposed to continue in occupation as tenant. She has however, not given written notice as required by that provision. The learned District Judge has followed the decision in Abdul Hafeel v. Muttu Bathool [1 (1957) 58 N.L.R. 409.] and held that as there was no written notice and no fresh contract of tenancy, the defendant was not entitled to occupy the premises.
 In Abdul Hafeel v. Muttu Bathool, Basnayake, C.J. held that by reason of the death on the 6th March, 1951 of one Cader who was a monthly tenant the contract of tenancy terminated on 31st March, 1951. With respect I do not think that that decision is correct. It is a general rule of our common law
191
that contracts bind the personal representative of the parties. Wessels Vol. I. P. 488 section 1655 has the following:
             "As a general rule contracts cannot bind a person who is not a party to it - res inter alias acta aliis necoocet nee prodest (Third parties can be neither injured nor benefited by the acts of parties) but according to our law a personal representative of a party to a contract is as much bound by the contract as the original party (C.8.38.13).
 In respect of a contract of letting and hiring, Voet 19.2.14 states;
 "From this contract springs a two-fold action, namely on letting and that on hiring. The action on a hiring is a personal bona fide action which is granted to the lessee and to his heir against the lessor and against his heir".
 Grotius  3-19-16 states:
 "It may be collected from the general law of contracts, that the right of letting and hiring and of entry and ouster, remains in and goes to the heirs of the lessor and lessee".
 Van Leeuwan's Roman Dutch Law 4-21 Kotze Vol. II p. 173 says:
 
10/31/2020 Ariyanandhi V. Mohamed Sideek
https://www.lawlanka.com/lal/pages/popUp/printNLRCaseReportPopUp.jsp?caseId=NLR80V186 3/4
"If the tenant or lessor dies during the continuance of the lease, his heirs must carry out the contract". Nathan, Common Law of South Africa Vol. II, p. 829, section 980 states:"The remedy which lies in favour of the lessee is known as the action conduct (action of hiring). It is a personal remedy, and lies in favour of the lessee, his heir or legal representative, against the lessor, his heir or legal representative. It claims as against a lessor of property that he shall give the plaintiff the use of such property, together with all such things as conducive to the use thereof. It appears to me therefore that the statement at page 102 of Lee and Honore's Law of Obligations which Basnayake, C.J. did not find possible to accept is correct. The passage at Lee and Honore's is as follows:"389. Effect of death of parties. In the absence of agreement to the contrary, the rights and duties of the lessor and of the lessee are (normally) transmitted on death to their representatives; but a lease expressed to be at the will of either party is determined by that party's death".
192
As stated in the above passage the exception to the rule that rights and duties are transmitted on death is where a lease is expressed to be at the will of either party, While, Landlord and Tenant, 4th Ed. P. 44 sets out what such a lease is:
 Lease at will of the landlord - A lease may be agreed to be at the will of the landlord in which the landlord may terminate the lease at any time he pleased without giving any previous notice to the tenant. Such a lease, or tenancy "at will", also terminate ipso jure on the death of the landlord.
 "Lease at will of the tenant-A lease may be validly made for as long as the tenant pleases. In such a case it is the tenant who has the right of choosing when to terminate the lease, and the landlord is not entitled to terminate it by giving notice".
 These two forms of leases are different to a monthly tenancy which may be terminated by either party by reasonable notice which with us has been held to be a calendar month's notice.
 By a contract of letting and hiring (Lacatio conduction) is understood a transaction by which one party binds himself to let the other party have the use of a certain thing for a certain time in consideration of a certain rent which the other party binds himself to pay to him, vide van Der Linden: Institutes of Holland (Juta's translation) p. 141. The letting had to be for a time for if it was in perpetuity, it would be emphyteusis or usufruct or something else. But the time need not necessarily be fixed in terms of years, months or days. Kensdorp: Institute of Cape Law, Vol. Ill, p. 208, states:
 "The term of the lease may, in a similar way, be either a period defined in the contract or one which may become defined later on by reference to some subsequent occurrence such as the giving of a certain notice by one or other of the parties or by the happening of some other event which may possibly be beyond the control of either."
 Grotius 3 - 19-8-9 ( Herbets Translation) are:
 Sec. VIII - The letting cannot be effected otherwise than for a time, for otherwise it would be an usufruct, or something else, but, if the time had been mentioned, it would, in cases of land, be understood for one year. In case of a house until the one or the other should renounce the hiring; which nevertheless, must take place at a proper time, so that the lessor may have the opportunity of letting his house, and the lessee of providing himself with another house.
193
Sec. II But a person may also let for as long as he pleases which letting is understood to expire by death, although other lettings, in which time is fixed, are valid after the death of the lessee, and go over to his heirs.
 In Abdul Hafeel v. Muttu Bathool, Basnayake, C.J. said 
 "The term fixed in a monthly tenancy is the end of the month." With respect I agree but subject to the qualification that where notice of termination is not given, the lease will not expire at the end of the month but will continue for a further period. Accordingly, where a monthly tenant dies in the course of the month and notice of termination has not been given, the contract of tenancy will not in my opinion, terminate at the end of the month but be continued between the lessor and the legal representative or heir of the tenant. In M. I. S. Fernando v. H. M. de Silva, [2 (1966)69 N.L.R. 164.] Manicavasagar, J. held that the death of the landlord does not terminate a contract of monthly tenancy and that his rights and obligations pass to his heirs. The reasoning and basis for his decision, however, are in some respects different to what I have set out above.
 I am, therefore, of the view that on the facts and circumstances of this case the contract of tenancy did not end at the death of Lucihamy on 3rd May, 1966 but that in the absence of any notice of termination it continued in force: accordingly the defendant's occupation thereafter was justified particularly as she offered to pay rent to the landlord A. M. M. Sideek, and, on his refusal to accept, deposited it with the Municipal Council. Though the plaintiff was a minor at the time when his father A. M. M. Sideek first let out the premises to Lucihamy, he had become a major by the time of her death and he had at all times acquiesced in and consented to the letting of the premises by his father; there are no differences between him and his father. In the circumstances, the plaintiff is bound by the letting made by A. M. M. Sideek and must abide by it and hold the premises subject to it. It follows that his allegation that the defendant was in wrongful and unlawful occupation since the date of the death of Lucihamy is unjustified and his action for a declaration of title necessarily fails.
 Even if the defendant has no right of claim to occupy the premises under the contract of tenancy and was only entitled to give notice under section 18 of the Rent Restriction Act (Cap. 274) as, for example, if she were a
194
dependant of Lucihamy and, in no wise an heir who was a member of her household for the relevant period, yet the plaintiff's action fails by reason of the operation of section 47 of the Rent Act No. 7 of 1972. The relevant part of that provision reads:
 "Notwithstanding anything in the Rent Restriction Act (Chapter 274) or in any other law 
 (a) any action or proceedings instituted in a court before the date of commencement of this Act 
 (i) (not relevant)
(ii) (not relevant)
(iii) for the ejectment from any residential premises of any person entitled under section 18 of the Rent Restriction Act (Chapter 274), to give notice to the landlord thereof to the effect that he proposes to continue in occupation of the premises as tenant thereof
10/31/2020 Ariyanandhi V. Mohamed Sideek
https://www.lawlanka.com/lal/pages/popUp/printNLRCaseReportPopUp.jsp?caseId=NLR80V186 4/4
shall, if such action or proceedings is or are pending on the date of commencement of this Act, be deemed at all times to have been and to be null and void;
Accordingly I allow the appeal, set aside the judgment and decree of the District Court and direct that order be entered dismissing plaintiff's action. The defendant-appellant will be entitled to her costs in both Courts.
'''
tr4w = txtrank()
tr4w.analyze(text, candidate_pos = ['NOUN', 'PROPN'], window_size=4, lower=False)
tr4w.get_keywords(10)