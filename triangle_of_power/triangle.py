from helpers import *

import numbers

from mobject.tex_mobject import TexMobject
from mobject import Mobject

from animation.animation import Animation
from animation.transform import *
from animation.simple_animations import *
from animation.playground import *
from topics.geometry import *
from topics.characters import *
from topics.functions import *
from topics.number_line import *
from scene import Scene

from mobject.svg_mobject import *
from mobject.vectorized_mobject import *
from mobject.tex_mobject import *

OPERATION_COLORS = [YELLOW, GREEN, BLUE]

def get_equation(index, x = 2, y = 3, z = 8, expression_only = False):
    assert(index in [0, 1, 2])
    if index == 0:
        tex1 = "\\sqrt[%d]{%d}"%(y, z), 
        tex2 = " = %d"%x
    elif index == 1:
        tex1 = "\\log_%d(%d)"%(x, z), 
        tex2 = " = %d"%y
    elif index == 2:
        tex1 = "%d^%d"%(x, y), 
        tex2 = " = %d"%z
    if expression_only:
        tex = tex1
    else:
        tex = tex1+tex2
    return TexMobject(tex).highlight(OPERATION_COLORS[index])

def get_inverse_rules():
    return map(TexMobject, [
        "x^{\\log_x(z)} = z",
        "\\log_x\\left(x^y \\right) = y",
        "\\sqrt[y]{x^y} = x",
        "\\left(\\sqrt[y]{z}\\right)^y = z",
        "\\sqrt[\\log_x(z)]{z} = x",
        "\\log_{\\sqrt[y]{z}}(z) = y",
    ])

def get_top_inverse_rules():
    result = []
    pairs = [#Careful of order here!
        (0, 2),
        (0, 1),
        (1, 0),
        (1, 2),
        (2, 0),
        (2, 1),
    ]
    for i, j in pairs:
        top = get_top_inverse(i, j)
        char = ["x", "y", "z"][j]
        eq = TexMobject("= %s"%char)
        eq.scale(2)
        eq.next_to(top, RIGHT)
        diff = eq.get_center() - top.triangle.get_center()
        eq.shift(diff[1]*UP)
        result.append(VMobject(top, eq))
    return result


def get_top_inverse(i, j):
    args = [None]*3
    args[i] = ["x", "y", "z"][i]
    big_top = TOP(*args)
    args[j] = ["x", "y", "z"][j]
    lil_top = TOP(*args)
    big_top.set_value(j, lil_top)
    return big_top

class TOP(VMobject):
    CONFIG = {
        "triangle_height_to_number_height" : 3,
        "offset_multiple" : 1.2,
        "radius" : 1.5,
        "propogate_style_to_family" : False,
    }
    def __init__(self, x = None, y = None, z = None, **kwargs):
        digest_config(self, kwargs, locals())
        VMobject.__init__(self, **kwargs)

    def generate_points(self):
        vertices = [
            self.radius*rotate_vector(RIGHT, 7*np.pi/6 - i*2*np.pi/3)
            for i in range(3)
        ]
        self.triangle = Polygon(
            *vertices, 
            color = WHITE,
            stroke_width = 5
        )
        self.values = [VMobject()]*3
        self.set_values(self.x, self.y, self.z)

    def set_values(self, x, y, z):
        for i, mob in enumerate([x, y, z]):
            self.set_value(i, mob)

    def set_value(self, index, value):
        self.values[index] = self.put_on_vertex(index, value)
        self.reset_submobjects()

    def put_on_vertex(self, index, value):
        assert(index in [0, 1, 2])
        if value is None:
            value = VectorizedPoint()
        if isinstance(value, numbers.Number):
            value = str(value)
        if isinstance(value, str):
            value = TexMobject(value)
        if isinstance(value, TOP):
            return self.put_top_on_vertix(index, value)
        value.scale_to_fit_height(self.get_value_height())
        value.center()
        if index == 0:
            offset = -value.get_corner(UP+RIGHT)
        elif index == 1:
            offset = -value.get_bottom()
        elif index == 2:
            offset = -value.get_corner(UP+LEFT)
        value.shift(self.offset_multiple*offset)
        anchors = self.triangle.get_anchors_and_handles()[0]
        value.shift(anchors[index])
        return value

    def get_surrounding_circle(self, color = YELLOW):
        return Circle(
            radius = 1.7*self.radius,
            color = color
        ).shift(
            self.triangle.get_center(),
            (self.triangle.get_height()/6)*DOWN
        )

    def put_top_on_vertix(self, index, top):
        top.scale_to_fit_height(2*self.get_value_height())
        top_anchors = list(
            top.triangle.get_anchors_and_handles()[0][:3]
        )
        top_anchors[index] = 0
        start = reduce(op.add, top_anchors)/2
        end = self.triangle.get_anchors_and_handles()[0][index]
        top.shift(end-start)
        return top

    def get_value_height(self):
        return self.triangle.get_height()/self.triangle_height_to_number_height

    def reset_submobjects(self):
        self.submobjects = [self.triangle] + self.values
        return self


class IntroduceNotation(Scene):
    def construct(self):
        top = TOP()
        equation = TexMobject("2^3 = 8")
        equation.to_corner(UP+LEFT)
        two, three, eight = [
            top.put_on_vertex(i, num)
            for i, num in enumerate([2, 3, 8])
        ]

        self.play(FadeIn(equation))
        self.dither()
        self.play(ShowCreation(top))
        for num in two, three, eight:
            self.play(ShowCreation(num), run_time=2)
        self.dither()

class ShowRule(Scene):
    args_list = [(0,), (1,), (2,)]

    @staticmethod
    def args_to_string(index):
        return str(index)
        
    @staticmethod
    def string_to_args(index_string):
        result =  int(index_string)
        assert(result in [0, 1, 2])
        return result

    def construct(self, index):
        equation = get_equation(index)
        equation.to_corner(UP+LEFT)
        top = TOP(2, 3, 8)
        new_top = top.copy()
        equals = TexMobject("=").scale(1.5)
        new_top.next_to(equals, LEFT, buff = 1)
        new_top.values[index].next_to(equals, RIGHT, buff = 1)
        circle = Circle(
            radius = 1.7*top.radius, 
            color = OPERATION_COLORS[index]
        )
        

        self.add(equation, top)
        self.dither()
        self.play(
            Transform(top, new_top),
            ShowCreation(equals)
        )

        circle.shift(new_top.triangle.get_center_of_mass())
        new_circle = circle.copy()
        new_top.put_on_vertex(index, new_circle)
        self.dither()
        self.play(ShowCreation(circle))
        self.dither()
        self.play(
            Transform(circle, new_circle),
            ApplyMethod(new_top.values[index].highlight, circle.color)
        )
        self.dither()


class AllThree(Scene):
    def construct(self):
        tops = []
        equations = []
        args = (2, 3, 8)
        for i in 2, 1, 0:
            new_args = list(args)
            new_args[i] = None
            top = TOP(*new_args)
            # top.highlight(OPERATION_COLORS[i])
            top.shift(i*5*LEFT)
            equation = get_equation(i, expression_only = True)
            equation.scale(2)
            equation.next_to(top, DOWN, buff = 0.7)
            tops.append(top)
            equations.append(equation)
        VMobject(*tops+equations).center()
        name = TextMobject("Triangle of Power")
        name.to_edge(UP)

        for top, eq in zip(tops, equations):
            self.play(FadeIn(top), FadeIn(eq))
        self.dither(3)
        self.play(Write(name))
        self.dither()

class SixDifferentInverses(Scene):
    def construct(self):
        rules = get_inverse_rules()
        vects = it.starmap(op.add, it.product(
            [3*UP, 0.5*UP, 2*DOWN], [2*LEFT, 2*RIGHT]
        ))
        for rule, vect in zip(rules, vects):
            rule.shift(vect)
        general_idea = TexMobject("f(f^{-1}(a)) = a")

        self.play(Write(VMobject(*rules)))
        self.dither()
        for s, color in (rules[:4], GREEN), (rules[4:], RED):
            mob = VMobject(*s)
            self.play(ApplyMethod(mob.highlight, color))
            self.dither()
            self.play(ApplyMethod(mob.highlight, WHITE))
        self.play(
            ApplyMethod(VMobject(*rules[::2]).to_edge, LEFT),
            ApplyMethod(VMobject(*rules[1::2]).to_edge, RIGHT),
            GrowFromCenter(general_idea)
        )
        self.dither()

        top_rules = get_top_inverse_rules()
        for rule, top_rule in zip(rules, top_rules):
            top_rule.scale_to_fit_height(1.5)
            top_rule.shift(rule.get_center())
        self.play(*map(FadeOut, rules))
        self.remove(*rules)
        self.play(*map(GrowFromCenter, top_rules))
        self.dither()
        self.remove(general_idea)
        rules = get_inverse_rules()
        original = None
        for i, (top_rule, rule) in enumerate(zip(top_rules, rules)):
            rule.center().to_edge(UP)
            rule.highlight(GREEN if i < 4 else RED)
            self.add(rule)
            new_top_rule = top_rule.copy().center().scale(1.5)
            anims = [Transform(top_rule, new_top_rule)]
            if original is not None:
                anims.append(FadeIn(original))
            original = top_rule.copy()
            self.play(*anims)
            self.dither()
            self.animate_top_rule(top_rule)
            self.remove(rule)

    def animate_top_rule(self, top_rule):
        lil_top, lil_symbol, symbol_index = None, None, None
        big_top = top_rule.submobjects[0]
        equals, right_symbol = top_rule.submobjects[1].split()
        for value in big_top.values:
            if isinstance(value, TOP):
                lil_top = value
                i = big_top.values.index(lil_top)
                lil_symbol = lil_top.values[i]
            elif isinstance(value, TexMobject):
                symbol_index = big_top.values.index(value)
                
        assert(lil_top is not None and lil_symbol is not None)
        cancel_parts = [
            VMobject(top.triangle, top.values[symbol_index])
            for top in lil_top, big_top
        ]
        new_symbol = lil_symbol.copy()
        new_symbol.replace(right_symbol)
        vect = equals.get_center() - right_symbol.get_center()
        new_symbol.shift(2*vect[0]*RIGHT)
        self.play(
            Transform(*cancel_parts, rate_func = rush_into)
        )
        self.play(
            FadeOut(VMobject(*cancel_parts)),
            Transform(lil_symbol, new_symbol, rate_func = rush_from)
        )
        self.dither()
        self.remove(lil_symbol, top_rule, VMobject(*cancel_parts))


class SixSixSix(Scene):
    def construct(self):
        randy = Randolph(mode = "pondering").to_corner()
        bubble = ThoughtBubble().pin_to(randy)
        rules = get_inverse_rules()
        sixes = TexMobject(["6", "6", "6"], next_to_buff = 1)
        sixes.to_corner(UP+RIGHT)
        sixes = sixes.split()
        speech_bubble = SpeechBubble()
        speech_bubble.pin_to(randy)
        speech_bubble.write("I'll just study art!")

        self.add(randy)
        self.play(ShowCreation(bubble))
        bubble.add_content(VectorizedPoint())
        for i, rule in enumerate(rules):
            if i%2 == 0:
                anim = ShowCreation(sixes[i/2])
            else:
                anim = Blink(randy)
            self.play(
                ApplyMethod(bubble.add_content, rule),
                anim
            )
            self.dither()
        self.dither()
        words = speech_bubble.content
        equation = bubble.content
        speech_bubble.clear()
        bubble.clear()
        self.play(
            ApplyMethod(randy.change_mode, "angry"),
            Transform(bubble, speech_bubble),
            Transform(equation, words),
            FadeOut(VMobject(*sixes))
        )
        self.dither()

class AdditiveProperty(Scene):
    def construct(self):
        exp_rule, log_rule = self.write_old_style_rules()
        t_exp_rule, t_log_rule = self.get_new_style_rules()

        self.play(
            ApplyMethod(exp_rule.to_edge, UP),
            ApplyMethod(log_rule.to_edge, DOWN, 1.5)
        )
        t_exp_rule.next_to(exp_rule, DOWN)
        t_exp_rule.highlight(GREEN)
        t_log_rule.next_to(log_rule, UP)
        t_log_rule.highlight(RED)
        self.play(
            FadeIn(t_exp_rule),
            FadeIn(t_log_rule),
            ApplyMethod(exp_rule.highlight, GREEN),
            ApplyMethod(log_rule.highlight, RED),
        )
        self.dither()
        all_tops = filter(
            lambda m : isinstance(m, TOP),
            t_exp_rule.split()+t_log_rule.split()
        )
        self.put_in_circles(all_tops)
        self.highlight_appropriate_parts(t_exp_rule, t_log_rule)




    def write_old_style_rules(self):
        start = TexMobject("a^x a^y = a^{x+y}")
        end = TexMobject("\\log_a(xy) = \\log_a(x) + \\log_a(y)")
        start.shift(UP)
        end.shift(DOWN)
        a1, x1, a2, y1, eq1, a3, p1, x2, y2 = start.split()
        a4, x3, y3, eq2, a5, x4, p2, a6, y4 = np.array(end.split())[
            [3, 5, 6, 8, 12, 14, 16, 20, 22]
        ]
        start_copy = start.copy()
        self.play(Write(start_copy))
        self.dither()
        self.play(Transform(
            VMobject(a1, x1, a2, y1, eq1, a3, p1, x2, a3.copy(), y2),
            VMobject(a4, x3, a4.copy(), y3, eq2, a5, p2, x4, a6, y4)
        ))
        self.play(Write(end))
        self.clear()
        self.add(start_copy, end)
        self.dither()
        return start_copy, end

    def get_new_style_rules(self):
        upper_mobs = [
            TOP("a", "x", "R"), Dot(), 
            TOP("a", "y", "R"), TexMobject("="), 
            TOP("a", "x+y")
        ]
        lower_mobs = [
            TOP("a", None, "xy"), TexMobject("="),
            TOP("a", None, "x"), TexMobject("+"),
            TOP("a", None, "y"),
        ]
        for mob in upper_mobs + lower_mobs:
            if isinstance(mob, TOP):
                mob.scale(0.5)
        for group in upper_mobs, lower_mobs:
            for m1, m2 in zip(group, group[1:]):
                m2.next_to(m1)
        for top in upper_mobs[0], upper_mobs[2]:
            top.set_value(2, None)
        upper_mobs = VMobject(*upper_mobs).center().shift(2*UP)
        lower_mobs = VMobject(*lower_mobs).center().shift(2*DOWN)
        return upper_mobs, lower_mobs

    def put_in_circles(self, tops):
        anims = []
        for top in tops:
            for i, value in enumerate(top.values):
                if isinstance(value, VectorizedPoint):
                    index = i
            circle = top.put_on_vertex(index, Circle(color = WHITE))
            anims.append(
                Transform(top.copy().highlight(YELLOW), circle)
            )
        self.add(*[anim.mobject for anim in anims])
        self.dither()
        self.play(*anims)
        self.dither()

    def highlight_appropriate_parts(self, t_exp_rule, t_log_rule):
        #Horribly hacky
        circle1 = t_exp_rule.split()[0].put_on_vertex(
            2, Circle()
        )
        top_dot = t_exp_rule.split()[1]
        circle2 = t_exp_rule.split()[2].put_on_vertex(
            2, Circle()
        )
        top_plus = t_exp_rule.split()[4].values[1]

        bottom_times = t_log_rule.split()[0].values[2]
        circle3 = t_log_rule.split()[2].put_on_vertex(
            1, Circle()
        )
        bottom_plus = t_log_rule.split()[3]
        circle4 = t_log_rule.split()[4].put_on_vertex(
            1, Circle()
        )

        mob_lists = [
            [circle1, top_dot, circle2],
            [top_plus],
            [bottom_times],
            [circle3, bottom_plus, circle4]
        ]
        for mobs in mob_lists:
            copies = VMobject(*mobs).copy()
            self.play(ApplyMethod(
                copies.highlight, YELLOW, 
                run_time = 0.5
            ))
            self.play(ApplyMethod(
                copies.scale_in_place, 1.2,
                rate_func = there_and_back
            ))
            self.dither()
            self.remove(copies)




class Test(Scene):
    def construct(self):
        TOP(2, 3, 8).highlight(BLUE).show()














