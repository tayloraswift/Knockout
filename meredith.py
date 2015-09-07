import text_t as comp
import channels

# create instance of Text
#text = comp.Text('<p class="h1">We begin our story in <em>New York</em>. There once was <strong>a girl</strong> known by everyone and no one. Her heart belonged to someone who couldn’t stay. </p><p>They loved each other recklessly.</p><p>They paid the price. She <em>danced</em> to forget him. He drove past her street every night. <em>She made <strong>friends and enemies</em>. He only</strong> saw her in his dreams. Then one day he came back. Timing is a funny thing. And everyone was watching. She lost him but she found herself and somehow that was everything.</p>')


#text.set_font(".fonts/Proforma-Semibold.otf", 1.3, 15)

tt = comp.Text('<p class="h1"><f class="strong">Marie-Joseph Paul Yves Roch </f class="strong"></p><p><f class="strong">Gilbert du Motier de Lafayette, Marquis de Lafayette</f class="strong"> (<f class="emphasis">6 September 1757 – 20 May 1834</f class="emphasis">), in the U.S. often known simply as <f class="strong">Lafayette</f class="strong">, was a French aristocrat and military officer who fought for the United States in the American Revolutionary War. A close friend of George Washington, Alexander Hamilton, and Thomas Jefferson, Lafayette was a key figure in the French Revolution of 1789 and the July Revolution of 1830. Born in Chavaniac, in the province of Auvergne in south central France, Lafayette came from a wealthy landowning family. He followed its martial tradition, and was commissioned an officer at age 13. He became convinced that the American cause in its revolutionary war was noble, and travelled to the New World seeking glory in it. There, he was made a major general, though initially the 19-year-old was not given troops to command. Wounded during the Battle of Brandywine, he still managed to organize an orderly retreat. He served with distinction in the Battle of Rhode Island. In the middle of the war, he returned home to lobby for an increase in French support. He again sailed to America in 1780, and was given senior positions in the Continental Army. In 1781, troops in Virginia under his command blocked forces led by Cornwallis until other American and French forces could position themselves for the decisive Siege of Yorktown.</p><p>Lafayette returned to France and, in 1787, was appointed to the Assembly of Notables convened in response to the fiscal crisis. He was elected a member of the <f class="emphasis">Estates-General</f class="emphasis"> of 1789, where representatives met from the three traditional orders of French society—the clergy, the nobility, and the commoners. He helped write the <f class="emphasis">Declaration of the Rights of Man and of the Citizen</f class="emphasis">, with the assistance of Thomas Jefferson. After the storming of the Bastille, Lafayette was appointed commander-in-chief of the National Guard, and tried to steer a middle course through the French Revolution. In August 1792, the radical factions ordered his arrest. Fleeing through the Austrian Netherlands, he was captured by Austrian troops and spent more than five years in prison.</p><p>Lafayette returned to France after Napoleon Bonaparte secured his release in 1797, though he refused to participate in Napoleon\'s government. After the Bourbon Restoration of 1814, he became a liberal member of the Chamber of Deputies, a position he held for most of the remainder of his life. In 1824, President James Monroe invited Lafayette to the United States as the nation\'s guest; during the trip, he visited all twenty-four states in the union at the time, meeting a rapturous reception. During France\'s July Revolution of 1830, Lafayette declined an offer to become the French dictator. Instead, he supported Louis-Philippe as king, but turned against him when the monarch became autocratic. Lafayette died on 20 May 1834, and is buried in Picpus Cemetery in Paris, under soil from Bunker Hill. For his accomplishments in the service of both France and the United States, he is sometimes known as "The Hero of the Two Worlds".</p><p>Lafayette was born on 6 September 1757 to Michel Louis Christophe Roch Gilbert Paulette du Motier, Marquis de La Fayette, colonel of grenadiers, and Marie Louise Jolie de La Rivière, at the château de Chavaniac, in Chavaniac, near Le Puy-en-Velay, in the province of Auvergne (now Haute-Loire).[2][a]</p><p>Lafayette\'s lineage appears to be one of the oldest in Auvergne. Members of the family were noted for their contempt for danger.[3] His ancestor Gilbert de Lafayette III, a Marshal of France, was a companion-at-arms who in 1429 led Joan of Arc\'s army in Orléans. Lafayette\'s great-grandfather (his mother\'s paternal grandfather) was the Comte de La Rivière, until his death in 1770 commander of the Mousquetaires du Roi, or Black Musketeers, King Louis XV\'s personal horse guard.[4] According to legend, another ancestor acquired the crown of thorns during the Sixth Crusade.[5] Lafayette\'s uncle Jacques-Roch died fighting the Austrians and the marquis title passed to his brother Michel.[6]</p><p>Lafayette\'s father died on 1 August 1759. Michel de Lafayette was struck by a cannonball while fighting a British-led coalition at the Battle of Minden in Westphalia.[7] Lafayette became marquis and Lord of Chavaniac, but the estate went to his mother.[7] Devastated by the loss of her husband, she went to live in Paris with her father and grandfather.[4] Lafayette was raised by his paternal grandmother, Mme de Chavaniac, who had brought the château into the family with her dowry.[6]</p><p>In 1768, when Lafayette was 11, he was summoned to Paris to live with his mother and great-grandfather at the comte\'s apartments in the Luxembourg Palace. The boy was sent to school at the Collège du Plessis, part of the University of Paris, and it was decided that he would carry on the family martial tradition.[8] The comte, the boy\'s great-grandfather, enrolled the boy in a program to train future Musketeers.[9] Lafayette\'s mother and her grandfather died, on 3 and 24 April 1770 respectively, leaving Lafayette an income of 25,000 livres. Upon the death of an uncle, the 12-year-old Lafayette inherited a handsome yearly income of 120,000 livres.[7]</p><p>In May 1771, Lafayette was commissioned a sous-lieutenant in the Musketeers. His duties were mostly ceremonial (he continued his studies as usual), and included marching in military parades, and presenting himself to King Louis.[10] The next year, Jean-Paul-François de Noailles, Duc d\'Ayen, was looking to marry off some of his five daughters. The young Lafayette, aged 14, seemed a good match for his 12-year-old daughter, Marie Adrienne Françoise, and the duc spoke to the boy\'s guardian (Lafayette\'s uncle, the new comte) to negotiate a deal.[11] However, the arranged marriage was opposed by the duc\'s wife, who felt the couple, and especially her daughter, were too young. The matter was settled by agreeing not to mention the marriage plans for two years, during which time the two spouses-to-be would meet from time to time, seemingly accidentally.[12] The scheme worked; the two fell in love, and were happy together from the time of their marriage in 1774 until her death in 1807.[13]</p><p>After the marriage contract was signed in 1773, Lafayette lived with his young wife in his father-in-law\'s house in Versailles. He continued his education, both at the riding school at Versailles (his fellow students included the future Charles X) and at the prestigious Académie de Versailles. He was given a commission as a lieutenant in the Noailles Dragoons in April 1773,[14] the transfer from the royal regiment being done at the request of Lafayette\'s father-in-law.[15]<br><br><br></p><p><f class="strong">Finding a cause</f class="strong"></p><p>Statue of Lafayette in front of the Governor Palace in Metz, where he decided to join the American cause.</p>')


class Meredith(object):
    def __init__(self, tracts):
        self.tracts = tracts
        self.t = 0
        for tr in self.tracts:
            tr.deep_recalculate()
    
    def target_channel(self, x, y, radius):
        for t, tract in enumerate(self.tracts):
            for c, channel in enumerate(tract.channels.channels):  
                if y >= channel.railings[0][0][1] - radius and y <= channel.railings[1][-1][1] + radius:
                    if x >= channel.edge(0, y)[0] - radius and x <= channel.edge(1, y)[0] + radius:
                        return t, c
        return 0, 0
    
    def set_t(self, tindex):
        self.t = tindex
    
    def set_cursor_xy(self, x, y, c=None):
        self.tracts[self.t].cursor.set_cursor(
                self.tracts[self.t].target_glyph(x, y, c=c),
                self.tracts[self.t].text
                )
    def set_select_xy(self, x, y, c=None):
        self.tracts[self.t].select.set_cursor(
                self.tracts[self.t].target_glyph(x, y, c=c),
                self.tracts[self.t].text
                )
    
    def text(self):
        return self.tracts[self.t].text
    
    def selection(self):
        return self.tracts[self.t].cursor.cursor, self.tracts[self.t].select.cursor
    
    def at(self, relativeindex=0):
        return self.tracts[self.t].text[self.tracts[self.t].cursor.cursor + relativeindex]
    def at_select(self, relativeindex=0):
        return self.tracts[self.t].text[self.tracts[self.t].select.cursor + relativeindex]
            
    def cdelete(self, rel1, rel2):
        return self.tracts[self.t].delete(self.tracts[self.t].cursor.cursor + rel1, self.tracts[self.t].cursor.cursor + rel2)
    
    def active_cursor(self):
        return self.tracts[self.t].cursor.cursor
    def active_select(self):
        return self.tracts[self.t].select.cursor
            
    def match_cursors(self):
        self.tracts[self.t].match_cursors()
    
    def hop(self, dl):
        self.tracts[self.t].cursor.set_cursor(self.tracts[self.t].target_glyph(self.tracts[self.t].text_index_location(self.tracts[self.t].cursor.cursor)[0], 0, (self.tracts[self.t].index_to_line(self.tracts[self.t].cursor.cursor) + dl) % len(self.tracts[self.t].glyphs) ), self.tracts[self.t].text)

    def add_channel(self):
        self.tracts[self.t].channels.add_channel()

tu = comp.Text('<p class="h1">We begin our story in <em>New York</em>. There once was <strong>a girl</strong> known by everyone and no one. Her heart belonged to someone who couldn’t stay. </p><p>They loved each other recklessly.</p><p>They paid the price. She <em>danced</em> to forget him. He drove past her street every night. <em>She made <strong>friends and enemies</em>. He only</strong> saw her in his dreams. Then one day he came back. Timing is a funny thing. And everyone was watching. She lost him but she found herself and somehow that was everything.</p>')
c1 = channels.Channel([[0, 850, False], [0, 1000, False]], [[300, 850, False], [300, 1000, False]])
c2 = channels.Channel([[350, 850, False], [350, 1000, False]], [[650, 850, False], [650, 1000, False]])
tu.channels = channels.Channels([c1, c2])
mere = Meredith([tt, tu])
