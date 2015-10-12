#import cProfile
#import interface

#cProfile.run('interface.main()')

import freetype
import timeit
import kevin

from text_t import character

t = '<p><f class="strong">Gilbert du Motier de Lafayette, Marquis de Lafayette</f class="strong"> (<f class="emphasis">6 September 1757 – 20 May 1834</f class="emphasis">), in the U.S. often known simply as <f class="strong">Lafayette</f class="strong">, was a French aristocrat and military officer who fought for the United States in the American Revolutionary War. A close friend of George Washington, Alexander Hamilton, and Thomas Jefferson, Lafayette was a key figure in the French Revolution of 1789 and the July Revolution of 1830. Born in Chavaniac, in the province of Auvergne in south central France, Lafayette came from a wealthy landowning family. He followed its martial tradition, and was commissioned an officer at age 13. He became convinced that the American cause in its revolutionary war was noble, and travelled to the New World seeking glory in it. There, he was made a major general, though initially the 19-year-old was not given troops to command. Wounded during the Battle of Brandywine, he still managed to organize an orderly retreat. He served with distinction in the Battle of Rhode Island. In the middle of the war, he returned home to lobby for an increase in French support. He again sailed to America in 1780, and was given senior positions in the Continental Army. In 1781, troops in Virginia under his command blocked forces led by Cornwallis until other American and French forces could position themselves for the decisive Siege of Yorktown.</p><p>Lafayette returned to France and, in 1787, was appointed to the Assembly of Notables convened in response to the fiscal crisis. He was elected a member of the <f class="emphasis">Estates-General</f class="emphasis"> of 1789, where representatives met from the three traditional orders of French society—the clergy, the nobility, and the commoners. He helped write the <f class="emphasis">Declaration of the Rights of Man and of the Citizen</f class="emphasis">, with the assistance of Thomas Jefferson. After the storming of the Bastille, Lafayette was appointed commander-in-chief of the National Guard, and tried to steer a middle course through the French Revolution. In August 1792, the radical factions ordered his arrest. Fleeing through the Austrian Netherlands, he was captured by Austrian troops and spent more than five years in prison.</p><p>Lafayette returned to France after Napoleon Bonaparte secured his release in 1797, though he refused to participate in Napoleon\'s government. After the Bourbon Restoration of 1814, he became a liberal member of the Chamber of Deputies, a position he held for most of the remainder of his life. In 1824, President James Monroe invited Lafayette to the United States as the nation\'s guest; during the trip, he visited all twenty-four states in the union at the time, meeting a rapturous reception. During France\'s July Revolution of 1830, Lafayette declined an offer to become the French dictator. Instead, he supported Louis-Philippe as king, but turned against him when the monarch became autocratic. Lafayette died on 20 May 1834, and is buried in Picpus Cemetery in Paris, under soil from Bunker Hill. For his accomplishments in the service of both France and the United States, he is sometimes known as "The Hero of the Two Worlds".</p><p>Lafayette was born on 6 September 1757 to Michel Louis Christophe Roch Gilbert Paulette du Motier, Marquis de La Fayette, colonel of grenadiers, and Marie Louise Jolie de La Rivière, at the château de Chavaniac, in Chavaniac, near Le Puy-en-Velay, in the province of Auvergne (now Haute-Loire).[2][a]</p><p>Lafayette\'s lineage appears to be one of the oldest in Auvergne. Members of the family were noted for their contempt for danger.[3] His ancestor Gilbert de Lafayette III, a Marshal of France, was a companion-at-arms who in 1429 led Joan of Arc\'s army in Orléans. Lafayette\'s great-grandfather (his mother\'s paternal grandfather) was the Comte de La Rivière, until his death in 1770 commander of the Mousquetaires du Roi, or Black Musketeers, King Louis XV\'s personal horse guard.[4] According to legend, another ancestor acquired the crown of thorns during the Sixth Crusade.[5] Lafayette\'s uncle Jacques-Roch died fighting the Austrians and the marquis title passed to his brother Michel.[6]</p><p>Lafayette\'s father died on 1 August 1759. Michel de Lafayette was struck by a cannonball while fighting a British-led coalition at the Battle of Minden in Westphalia.[7] Lafayette became marquis and Lord of Chavaniac, but the estate went to his mother.[7] Devastated by the loss of her husband, she went to live in Paris with her father and grandfather.[4] Lafayette was raised by his paternal grandmother, Mme de Chavaniac, who had brought the château into the family with her dowry.[6]</p><p>In 1768, when Lafayette was 11, he was summoned to Paris to live with his mother and great-grandfather at the comte\'s apartments in the Luxembourg Palace. The boy was sent to school at the Collège du Plessis, part of the University of Paris, and it was decided that he would carry on the family martial tradition.[8] The comte, the boy\'s great-grandfather, enrolled the boy in a program to train future Musketeers.[9] Lafayette\'s mother and her grandfather died, on 3 and 24 April 1770 respectively, leaving Lafayette an income of 25,000 livres. Upon the death of an uncle, the 12-year-old Lafayette inherited a handsome yearly income of 120,000 livres.[7]</p><p>In May 1771, Lafayette was commissioned a sous-lieutenant in the Musketeers. His duties were mostly ceremonial (he continued his studies as usual), and included marching in military parades, and presenting himself to King Louis.[10] The next year, Jean-Paul-François de Noailles, Duc d\'Ayen, was looking to marry off some of his five daughters. The young Lafayette, aged 14, seemed a good match for his 12-year-old daughter, Marie Adrienne Françoise, and the duc spoke to the boy\'s guardian (Lafayette\'s uncle, the new comte) to negotiate a deal.[11] However, the arranged marriage was opposed by the duc\'s wife, who felt the couple, and especially her daughter, were too young. The matter was settled by agreeing not to mention the marriage plans for two years, during which time the two spouses-to-be would meet from time to time, seemingly accidentally.[12] The scheme worked; the two fell in love, and were happy together from the time of their marriage in 1774 until her death in 1807.[13]</p><p>After the marriage contract was signed in 1773, Lafayette lived with his young wife in his father-in-law\'s house in Versailles. He continued his education, both at the riding school at Versailles (his fellow students included the future Charles X) and at the prestigious Académie de Versailles. He was given a commission as a lieutenant in the Noailles Dragoons in April 1773,[14] the transfer from the royal regiment being done at the request of Lafayette\'s father-in-law.[15]<br><br><br></p><p><f class="strong">Finding a cause</f class="strong"></p><p>Statue of Lafayette in front of the Governor Palace in Metz, where he decided to join the American cause.</p>'

tt = kevin.deserialize(t)

import fonttable

class Textline(object):
    def __init__(self, text, anchor, stop, y, c, l, startindex, paragraph, fontclass, leading):
        self._p = paragraph
        self._f = fontclass

        try:
            self._fontclass = fonttable.table.get_font(paragraph[0], tuple(fontclass))
        except KeyError:
            self._fontclass = fonttable.table.get_font(paragraph[0], () )

        # takes 1,989 characters starting from startindex
        self._sorts = text[startindex:startindex + 1989]
        
        # character index to start with
        self.startindex = startindex
        self.leading = leading
        
        # x positions
        self.anchor = anchor
        self.stop = stop
        
        # line y position
        self.y = y
        self.c = c
        self.l = l

    def build_line(self):
        
        p, p_i = self._p
        
        # go by syllable until you reach the end
        index = self.startindex
        
        # list that contains glyphs
        self.glyphs = []
        
        # start on the anchor
        x = self.anchor
        n = 0

        for entity in self._sorts:
            
            glyphanchor = x
            
            if type(entity) is list:
                glyph = entity[0]
                
                if glyph == '<p>':
                    if n > 0:
                        break
                    else:
                        # we don’t load the style because the outer function takes care of that
                        # retract x position
                        glyphanchor -= self._fontclass['fontsize']
                        glyphwidth = 0
                        x -= self._fontclass['tracking']

                elif glyph == '</p>':
                    self.glyphs.append((self._fontclass['fontmetrics'].character_index(glyph), x, self.y, self._p, tuple(self._f)))
                    # paragraph breaks are signaled by a negative index
                    return (self.startindex + len(self.glyphs))*-1 - 1
                    break

                elif glyph == '<f>':

                    # look for negative classes
                    if '~' + entity[1] in self._f:
                        self._f.remove('~' + entity[1])
                    else:
                        self._f.append(entity[1])
                        self._f.sort()
                        
                    try:
                        self._fontclass = fonttable.table.get_font(p, tuple(self._f))
                    except KeyError:
                        # happens if requested style is not defined
                        errors.styleerrors.add_style_error(tuple(self._f), self.l)
                        try:
                            self._fontclass = fonttable.table.get_font(p, () )
                        except AttributeError:
                            self._fontclass = fonttable.table.get_font('_interface', () )
                elif glyph == '</f>':

                    try:
                        self._f.remove(entity[1])
                        self._fontclass = fonttable.table.get_font(p, tuple(self._f))
                    except (ValueError, KeyError):
                        # happens if the tag didn't exist
                        self._f.append('~' + entity[1])
                        self._f.sort()
                        errors.styleerrors.add_style_error(tuple(self._f), self.l)
                        try:
                            self._fontclass = fonttable.table.get_font(p, () )
                        except AttributeError:
                            self._fontclass = fonttable.table.get_font('_interface', () )
            
            else:
                glyph = entity

            glyphwidth = self._fontclass['fontmetrics'].advance_pixel_width(glyph)*self._fontclass['fontsize']
            self.glyphs.append((self._fontclass['fontmetrics'].character_index(glyph), glyphanchor, self.y, self._p, tuple(self._f)))
            
            
            if glyph == '<br>':
                x -= self._fontclass['tracking']
                break
            
            x += glyphwidth + self._fontclass['tracking']
            n = len(self.glyphs)
            
            # work out line breaks
            if x > self.stop:
                if glyph == ' ':
                    pass
                
                elif ' ' in self._sorts[:n]:
                    i = n - 2
                    while True:
                        if self._sorts[i] == ' ':
                            del self.glyphs[i + 1:]
                            break
                        i -= 1
                else:
                    del self.glyphs[-1]
                break
                
        # n changes
        return self.startindex + len(self.glyphs)

def q():
    l = Textline(tt, 89, 389, 50, 0, 13, 0, ['body', 0], [], 22)
    l.build_line()

print(timeit.timeit("q()", number=10000, setup="from __main__ import q"))
