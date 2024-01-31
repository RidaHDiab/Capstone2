import string
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from DatabaseConnection import Database

db = Database()


def getArt(table_name, start_date, end_date):
    query = f"SELECT * FROM {table_name} WHERE publishedTime  BETWEEN '{start_date}' AND '{end_date}';"
    try:
        db.init()
        rows = db.db_execute(query)
        db.db_close()
        arts_list = [list(row) for row in rows]
        return arts_list
    except Exception as e:
        print(f"failed to retrieve data from {table_name} ", e)


class Compare:

    @staticmethod
    def compareTtfid(text1, text2):
        print("TEXT1", text1, "\n", "TEXT2:", text2)
        text1 = text1.translate(str.maketrans("", "", string.punctuation)).lower()
        text2 = text2.translate(str.maketrans("", "", string.punctuation)).lower()

        tfidf_vectorizer = TfidfVectorizer()
        tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
        cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])

        print("Cosine similarity using TFid:", cosine_sim[0][0])

        return cosine_sim[0][0]

    @staticmethod
    def initCompare(title, body, description, publishedTime):
        com = Compare()
        start_date = publishedTime - timedelta(weeks=4)
        end_date = publishedTime + timedelta(weeks=4)
        may_art = getArt("may_art", start_date, end_date)
        bbc_art = getArt("bbc_art", start_date, end_date)
        may_description_sim = []
        bbc_b_sim = []
        bbc_id = None
        may_id = None
        for b in [row_list[3] for row_list in may_art]:
            may_description_sim.append(com.compareTtfid(body, b))
        if may_description_sim:
            max_description_index, max_description_value = max(enumerate(may_description_sim), key=lambda x: x[1])
            if max_description_value >= 0.65:
                may_id = may_art[max_description_index][0]

        for b in [row_list[3] for row_list in bbc_art]:
            bbc_b_sim.append(com.compareTtfid(body, b))

        if bbc_b_sim:
            max_b_index, max_b_value = max(enumerate(bbc_b_sim), key=lambda x: x[1])
            if max_b_value >= 0.65:
                bbc_id = bbc_art[max_b_index][0]
        return may_id, bbc_id


def main():
    may_art = 'The Deputy Chief of the Political Bureau of the Hamas movement, Saleh al-Arouri, was martyred on Tuesday evening, as a result of an attack that targeted the Southern Suburb of Beirut.Lebanons National News Agency reported that "an Israeli drone targeted an office of the Hamas movement in Msharafieh" while "ambulances reached the area to transport casualties."Al Mayadeens correspondent reported that an Israeli drone targeted the building with three missiles, resulting in the martyrdom of six individuals.He added, "Medical teams, the army, and security forces are working to remove the rubble left by the Israeli raid on the building in the southern suburb."The Islamic Resistance Movement, Hamas, mourned the "great national leader," Saleh al-Arouri, who commanded the Resistance in the West Bank and the Gaza Strip and was the architect of Operation Al-Aqsa Flood.The late martyr and leader had previously discussed in an interview for Al Mayadeen increasing Israeli death threats against him. When asked about the issue, martyr al-Arouri said, "The Israeli threat against me will not change my convictions, and it will not have an impact on the path [that I have chosen]."'
    jaz_art = 'Senior Hamas official Saleh al-Arouri has been killed in an Israeli drone strike on Beirut’s southern suburb of Dahiyeh, the Palestinian group and Lebanese media outlets say.Al-Arouri was killed on Tuesday in a “treacherous Zionist strike”, Hamas said on its official channel. Hamas politburo member Izzat al-Sharq called it a “cowardly assassination”.Al-Arouri was a senior official in Hamas’s politburo and was known to be deeply involved in its military affairs. He had previously headed the group’s presence in the occupied West Bank.Samir Findi Abu Amer and Azzam Al-Aqraa Abu Ammar, leaders of Hamas’ armed wing – the Qassam Brigades – were also killed, Hamas said in a message on its Telegram channel.It named four other members of the group who were also killed.Earlier, Lebanon’s state-run National News Agency said the blast killed at least six people and that it was carried out by an Israeli drone.Hamas said al-Arouri’s killing would not “undermine the continued brave resistance” in Gaza, where the Palestinian group’s fighters are battling Israeli ground forces.“It proves once more the utter failure of the enemy to achieve any of its aggressive goals in the Gaza Strip,” senior Hamas official Izzat al-Rishq said in a statement.The group’s top leader Ismail Haniyeh condemned the attack as a “terrorist act”, a violation of Lebanon’s sovereignty, and an expansion of Israel’s circle of hostility against Palestinians.Haniyeh said in televised remarks that Hamas “will never be defeated”.There was no immediate comment from Israel.Mark Regev, an adviser to Israeli Prime Minister Benjamin Netanyahu, told the United States news channel MSNBC that Israel had not taken responsibility for the attack but “whoever did it, it must be clear that this was not an attack on the Lebanese state”.“Whoever did this did a surgical strike against the Hamas leadership,” Regev said in an interview.Lebanese Prime Minister Najib Mikati condemned the killing. His office said in a statement that the attack “aims to draw Lebanon into a new phase of confrontations” with Israel at a time when Hamas ally Hezbollah has been exchanging daily cross-border fire with Israeli forces in northern Israel, the statement said.Al Jazeera’s Zeina Khodr, reporting from Beirut, said there was “panic” in the Lebanese capital after the attack.“The targeted killing made many people here in the capital feel that this conflict could widen and could escalate, and all eyes are now on Hezbollah’s reaction,” Khodr said.Iran, which supports both Hamas and Hezbollah, said al-Arouri’s killing would create more resistance against Israel, its state media reported.“The martyr’s blood will undoubtedly ignite another surge in the veins of resistance and the motivation to fight against the Zionist occupiers not only in Palestine but also in the region and among all freedom seekers worldwide,” Iranian Ministry of Foreign Affairs spokesperson Nasser Kanaani said.Kanaani also condemned the violation of Lebanon’s sovereignty and territorial integrity.Netanyahu had threatened to kill al-Arouri long before Israel’s latest assault on the besieged Gaza Strip.Israeli political analyst Akiva Eldar told Al Jazeera the killing was a much needed success for Netanyahu.Imad Harb, director of research at the Arab Center Washington DC, agreed, saying Israel carried out the attack in search for what has become an elusive win.“So far, the Israelis have not been able to call a victory in Gaza, so assassinating Hamas leaders is partly something that they wanted to do anyway,” he told Al Jazeera. “This is an achievement for the Israeli army and for the Israeli politicians.”Since Israeli forces and Hezbollah began exchanging fire across the Lebanese-Israeli border on October 8, the fighting has largely been concentrated a few kilometres inside each country. But on several occasions, Israel’s air force has hit what it said were Hezbollah positions deeper inside Lebanon.Harb said the killing of al-Arouri is a “dangerous escalation” because it took place in Hezbollah’s area of operations, far from the border.Harb predicted Hezbollah would likely step up attacks on Israel in response to the killing but would stop short of escalating the conflict into an all-out war.Meanwhile, at mosques in Arura, the hometown of the slain Hamas leader in the West Bank, Palestinians gathered to mourn al-Arouri’s death.Protests and gatherings also took place in Ramallah and several nearby towns, such as Deir Qaddis.A general strike in Ramallah has also been called for Wednesday.'
    bbc_art = 'Israel has insisted the assassination of a Hamas leader in Beirut was not an attack on Lebanon, as its enemies warned of "punishment" for his death.Israel has neither confirmed nor denied that it killed Saleh al-Arouri, but a spokesman called it a "surgical strike against the Hamas leadership".Hamas denounced it as a "terrorist act", while its ally Hezbollah said it was an assault on Lebanese sovereignty.Lebanons PM accused Israel of trying to "drag" it into a regional war.Lebanese media report that Arouri, a deputy political leader of Hamas, was killed in a drone strike in southern Beirut on Tuesday along with six others - two Hamas military commanders and four other members.He was a key figure in the Izzedine al-Qassam Brigades, Hamass armed wing, and a close ally of Ismail Haniyeh, the Hamas leader. He had been in Lebanon acting as a connection between his group and Hezbollah.There have been near daily exchanges of fire between Hezbollah and Israeli forces since the start of the war between Israel and Hamas in Gaza, but so far the violence has been limited to the area along the Israel-Lebanon border.Hezbollah - which, like Hamas, is considered a terrorist organisation by Israel, the UK and others - is the largest political and military force in Lebanon and has ministers in the countrys government.The Israel Defense Forces (IDF) refused to comment on the assassination of Saleh al-Arouri, but said its troops were "highly prepared for any scenario"."The IDF is in a very high state of readiness in all arenas, in defence and offence," spokesman Rear Adm Daniel Hagari told a briefing."The most important thing to say tonight is that we are focused and remain focused on fighting Hamas," he added.Israeli government adviser Mark Regev also stopped short of confirming Israel had carried out the attack, but he told MSNBC: "Whoever did it, it must be clear that this was not an attack on the Lebanese state."It was not an attack even on Hezbollah, the terrorist organisation."Whoever did this did a surgical strike against the Hamas leadership. Whoever did this has a gripe with Hamas. That is very clear."Arouri, 57, is the most senior Hamas figure to be killed since Israel went to war with the group after its 7 October attack.On that day, waves of Hamas gunmen invaded Israel and attacked communities around the border, killing about 1,200 people, mostly civilians, and taking around 240 to Gaza as hostages.Israel launched a military offensive in response, with the declared aim of destroying Hamas.Since then, more than 22,000 Palestinians - mostly women and children - have been killed in Israeli strikes on Gaza, according to Gazas Hamas-run health ministry.Lebanons state news agency said Arouri had been killed by an Israeli drone attack on a Hamas office in the southern Beirut suburb of Dahiyeh.A witness from Reuters news agency saw firefighters and paramedics gathered around a high-rise building where there was a large hole in what appeared to be the third floor.Video footage on social media showed a car in flames and extensive damage to buildings in what is a busy residential area.Dahiyeh is known as a stronghold of Hezbollah.Mr Haniyeh, the leader of Hamass political bureau, called the attack a "cowardly... terrorist act, a violation of Lebanons sovereignty, and an expansion of its circle of aggression".Hezbollah said that it considered Arouris death "to be a serious assault on Lebanon, its people, its security, sovereignty, and resistance, and the highly symbolic and significant political and security messages it contains".It said the attack was "a dangerous development in the course of the war... and we in Hezbollah affirm that this crime will never pass without response and punishment"."Its hand is on the trigger, and its resistors are in the highest levels of readiness and preparedness," it added.Iran, a major supporter of both groups, said Arouris killing would "undoubtedly ignite another surge in the veins of resistance".'
    com = Compare()
    jaz_bbc_sim = com.compareTtfid(jaz_art, bbc_art)
    jaz_my_sim = com.compareTtfid(jaz_art, may_art)

    print(jaz_my_sim, jaz_bbc_sim)


if __name__ == '__main__':
    main()
