#!/usr/bin/env python3
"""THE WORLD TODAY - front page for Friday, 20 November 2026.

A pure-standard-library newspaper renderer: a flat RGB bytearray canvas,
hand-rolled line/rect/circle painters, an embedded 1-bit bitmap font, and
a hand-written PNG encoder. No Pillow, no font files, no network, no clock,
no randomness - the same input always yields the same bytes.
"""
import base64
import os
import struct
import zlib

W = 1024
H = 1024
PAPER = (250, 247, 238)
INK = (22, 22, 22)
SOFT = (74, 74, 74)
WHITE = (255, 255, 255)
GOLD = (176, 132, 32)

CANVAS = bytearray([PAPER[0], PAPER[1], PAPER[2]] * (W * H))


def put(x, y, color):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        CANVAS[i] = color[0]
        CANVAS[i + 1] = color[1]
        CANVAS[i + 2] = color[2]


def fill_rect(x, y, w, h, color):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            CANVAS[i] = color[0]
            CANVAS[i + 1] = color[1]
            CANVAS[i + 2] = color[2]


def hline(x0, x1, y, thick, color):
    fill_rect(x0, y - thick // 2, x1 - x0, thick, color)


def vline(x, y0, y1, thick, color):
    fill_rect(x - thick // 2, y0, thick, y1 - y0, color)


def segment(x0, y0, x1, y1, color):
    """Bresenham line, endpoints inclusive."""
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        put(x0, y0, color)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def ring(cx, cy, r, color):
    """Midpoint circle outline."""
    x = 0
    y = r
    d = 3 - 2 * r
    while x <= y:
        for sx, sy in ((x, y), (y, x), (-x, y), (-y, x),
                       (x, -y), (y, -x), (-x, -y), (-y, -x)):
            put(cx + sx, cy + sy, color)
        if d < 0:
            d += 4 * x + 6
        else:
            d += 4 * (x - y) + 10
            y -= 1
        x += 1


def oval(cx, cy, rx, ry, color):
    """Ellipse outline by parametric sampling."""
    import math
    steps = max(48, int(2 * 3.14159 * max(rx, ry)))
    prev = None
    for k in range(steps + 1):
        a = 2 * 3.14159 * k / steps
        px = int(round(cx + rx * math.cos(a)))
        py = int(round(cy + ry * math.sin(a)))
        if prev is not None:
            segment(prev[0], prev[1], px, py, color)
        prev = (px, py)


def globe(cx, cy, r, color):
    """Small line-art globe: outer ring, two meridians, one parallel."""
    ring(cx, cy, r, color)
    oval(cx, cy, max(2, r // 3), r, color)
    oval(cx, cy, r, max(2, r // 3), color)
    hline(cx - r, cx + r, cy, 1, color)


# ---- embedded bitmap fonts ----
# Each entry: (size, ascent, charset, idx_len, blob_lines).
# Blob = base85(zlib(idx_bytes + bitmap_bytes)); idx holds 5 bytes per
# glyph in charset order: advance, width, height, bearing_x + 128,
# top_offset (baseline minus glyph top).
TABLES = {
    "mast": (66, 71, "ABCDEFGHIJKLMNOPQRSTUVWXYZ ", 135, (
        "c-qyO&yM6o62{Z*7Pho#U8}w9VKlBif%v2Dff<<7x)2A%X&-@pggJ6RI1vYU3wRW>r+thBaoD4gICyuxl^b7tk>zw%b&r4<U|L<@FRRLx&WsF4MrJ;IbmgzEuSKq|9{B4=c>Cs?BCowJ^5~I#_U^k<x_1w9|8JjOJ$#rh={mhc<ehiqx;Ng?(#~JM^_G-geN{fw>)w9*",
        "TB^rAKKSseX9W))r296`dFNai9sa5WpP?cC5C^AMD*jCTDTWMxO&EbKu}hc~y~6b~)Ehd5>-Hi=Lc7-wTeRsSp<xTPO_vFW_73<a0yW>Ez0#)5f)OZy?Sct#z;3~;U<(y;lYXC20MV5SFD1G0*u}WVEvGJ^)^>(UlSQSCs>4C0Nhdm<=<zjq4VBj1?Dbv~wDY1d`sI@<",
        "yE|(rwC1F@{m+@+_Mg|o7P4R3)6^=l3CD~B_XWoP(*kCaUwKzeP6nzSoeWSnx<2UtXd0n~T+jz-7vO%~psFMM*v6UKoKgQ1b+|*T6V=DzM)gSnA2UVE-H0wY?N<>T#$#~J44)}ySIMuVy9W;s!K_37fdjSj5v({XifGV*g~0%+Jckaq>t<qq25meG{~U1p{f=5TuQ26Z",
        "NgWG$r)dH+NJ;ZlBW*UQ1!o#E+FeyE)iTo}S8cSrP2JB`i3skO)o`TSJN4#7gZ56f3ThK7to1A`<DW&pp1GBNlA5=SONesSw>tB5t`~=rNY%l;W<0;HneYH3TuIc$7l1gZL_0k38uSEn0s@0XI7LWP(i+X3@OMF`oB{7*)DLA=!tahSCsgN9u7FlAaE6{hbY|ZHu>>G}",
        "1jI@Rb*^{4M$z!e!J1;+&*h<n$90SjU35<i62B6bDDnG4$EQ?mW)>9id49oOXt#Lkgmg(0sP096&C3g^tiDElR5(M)+%A{NGmn|doL{}Zp*2d*W+i8{(p%tFyhL0QHL)SK#BK%8w1DC4g1999NVG&p^!!0IAiTwYM@=>UOK2p-yNTZ!IL{(ES<uHEoh6-|rVULD#K<Jn",
        "pq3~JL|_H;0ec>iS<4r#I=?S<+6p?!|3=fquP}YzIf>^}c^P#29&{=f-D8n7!*np1K4x8X8NKo&;YTYD%D*H3Hh!fH$`6DsS&*aheHljM1vx3-TX;#%%H2Xo?rUX#AV2TpM%f+cj9)9;6AsGegkD*l(5+Y|?$<1i$#w@fGa3)FDndBM%*t8t9s^rVqt{ODTGP}uEnCBY",
        "h5*2fHLPUN2Oc&8dO{*jO+(b$UthC(#87KzLalu<jDUCv;1Xtq*c<2!QPIXPfhOUfKo$Q5lnJ^bE{@j6L{D@pv_!K)MU-%6c_1(`48Y;9{X*A4dxxA%F6*8CR@SsgI%G+W6hul$NN@-EC$p3WF=Rk8hD4@`36;X1!+@-)I)%Rt;T%q`Jg!q-RgTn%GDm8z^&#t6J0E&$",
        "eK$)~w2N8EY?dsT@-9Yg+l!c%y@K_QM7}Q(ZrPUzPu-WeeUBo)OV$Q$PaAAnDs19;Uh$VR$5Enx&f%(G<Z$KlcDV2~hdcH=f6niY9IjxGjvX%K4%Y~VgOwyCs>5~V$fZoU73B&A2f*MGY*Ucvh=x0F6}JHku6o?Eqg1L>n@5>LGqD(mK#a^U)|h@K#;nf69fs`g4b!1^",
        "&a$Z~Van0-@$A|7&R{=JusRJxhKhHuR^2R*n#*k!L%-*`Kf;2(;1W~ph%LGM*pd4LIjdYZ6xel<q3y;B(yRqT5Fmr}vcufE(ZoX}K(J0mQiA2Fc!9L6LM$qy=6F#Ttk}RqO4r!eXfJ-)@z*nkcP<8LdV`f|D=Es{slZhsh-=j%qdclA4Vu;rSgCtio!*y<-D9cv8|!Y5",
        "tZ9_4PQ~~Hp7-$$^f7gS{)Ornt?$<4!7rH3`3^{cWrjWuNW2|aDeflC`s?TR#m6qeoyRI50sat|+WBmFvRQYTfZ^q3++z(?4*HmSjTmlGHs)fb%Me{A<rxHXLMjtOJt)CB$wrS!Hg;Ho$iCGLqJ#2;MCO29($coCgHKwRj@qmrv=Kin-a=dS|54=z*?g?+bgT_^TojwN",
        "Jr;Gkw}A{Ai6Mf(sHLEXG)xw?G^f#ORwd8Uo~6l3XsjI^txGc5(S}Rum6(opUg6}z(gjbVmQu-YrSyIrE_o!il-@g(3Qloi{m(QThwXh<8m(lrUKKxc{kYN6H+gB=*uer#UdDfj>ut64ofvwn<Fk~4d1Mj4m(os4KT6kk+VvmBFgu%Sn}a!Q53$cnc8b=I=@_ufOXaze",
        "ozMmB|G@-Ur;C&CF`gP&ZkBVj!^s(wQym1sh2yG~xa8hvO=qP=0?jef0^{zG)1fE&!}ve9cx85r3~kyp&9_&pG+>sYj6BO6d5CGZn0b0>=as7y$}SyE>M3M?3p;+?EJ=`_G?ol6nv8M-s2J2x<=|kpUZ>`O{6<%ra`nfYRiChxTUKb;F^KF^)AiZq(_oK6!5)~yU(h-i",
        ">8Mq$bGd*E%!I{On^jV`JvSVyQJMW>Ib9JiNcVjnNH_BIMeI)Nk%vSaq{CiSyZ2I3cD$$VHR8_hW!2g?;i#o9(<{?(bS~K1J^i5>RJtM!VY6+%BpDBystjkUtWT=kn4-#!R%WV|T~oEnC#s{Sj3YMXDpBM={|5lC9@_",
    )),
    "head": (36, 39, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.-'\u2019\u2014$%:", 230, (
        "c-pO3!H(ND5FLTQ60Hp}hfU&a9J5J^^qQjz2x32FfgW<KZ*>8~WUz-E`v=W0^w?Xu@WIFZgs9j<j#aThqacdeH<V<nn`|~))Ozp1mZ%{)91h3#r$_E+GU;Wy`+4V1|MS5ENSd;!$M)#xe&6KLqrOR$yLaQa$L{Ff5x(8N-M72XZ^U~~zJVO^w|n>cr-z3(l`n`KjYea4",
        "Fd7}OjNSOlFYzGC*H1=vba<%U^x;GN9E}d$A!#Dgj>z=%L_ac1qSxR#v!Y}To`TP75=;k%h9r}gl+vnWK~pl31z8_XL&>y(Y$(;HQl~Y;H$CFdb)|x5;EQjcuKtbKcwO62+2F{O6l(Fdk>yhPLb+VK470#w%oWgant%fQfh@<OUcv}Wu|e1+n8%|AT!9AEOm~T1#Y^|R",
        "^xSmsu3B5L$+p`*FnmmIp?ub3qCD*Z4*|nF9mWyUh}?!I;yP=eGT1?vWE%$QiYRO;sV#|8lZ<m$aM(D82ZxEd%p{bNWSzks&2%l<2a<`WNn@gI?!(qtKv0(-^W7ze(DJ%=9oc4Y-`2L)rShM5>5|)<t=XzdmjCI372^WcJVVEXO?V*(7vLN$Nu9#$YXsm1JR?%CKtx7M",
        "JUc_14YP~JQzl2`HWD^r+hCRoL|43kpIF|jL+OKPsuB#FMOOly)uQP|Hk39|4j{`EvWhZ>6jO+aGJ)uf<u{gJA*$L*36Xoj*3jZ~OLo0Rzv~l-GnMrQks+Nbg;SN_5s+#Gx&~LE1r4ZAz%|T*@|;p}0luR&3CKV_EoeX;FN<ilUbYzy`(D(@TxHSja;Lis-)O&wuVR-M",
        "`ZqZGqAj+`wz-cs<LQrNyg}XrHf`#=Zhw9-YIEaJn|(HG-{Mi@uBcX&@TifeNTVM$phW(cxG(TL!5-$U-sMZZ?xXV)<Os&u5u=;A=^~u(F;9m!Rvh8fM>x8Z*!?g4O!@*4fGgUB?m3xgyc2K?If7*z393Zy%0#&k<uYQ0>HX|<Ajw&H3)HJwxk@7r0GwDi19#^E<cmn;",
        "9E>~tUnu<;?w-Qc3#>;KXBn#Cm<AKa!5yjG1nsj(>7U}Ad88<hv6f|IQh7?=wxqX6;O{^<3Y(&(iA&jX#!EkyO%&scq}J%JVkxz=ggn|xf-GmBd+7tD{4>hhi9gODe{G_ilejoJr{v<~H6`y(-awMSVV`3s$`%(q+3aLVz!Iy@xy>T~AWq>0S>~8Y2F`IRVMYxi@jYf^",
        "-F^mr#bSM|R+3Fysc?lN6XY56FhhR^Qx7M>NA@1|1CRFJ>^<3gvF<$he&D^K=Y}+`XGJI@O=y5TsdG_hn20PhRo>z~9m^0C8zZ6`%nTjz1``!}AFGn{Glm5iTDEr3Kq4)_B#pf*UD56c27>(K7_{+t1ux=t$wxdp9Q|^3Z>VS}ZwPstZU`)<4j#bBHGGVMPq~$HsK|0Y",
        "TG~=87G(&qoG2rj6Tzz<<s+)b?^5zp@>$|-*hBW#RvM;U&ejH|3f{|@1$&RHIgc&S;;Hm=$>q>Oxx%m!S@+eSjR=&yqU0rs-$@ucz}aAEj9S&u#L!bib3?}n6;!OeeuLuCI;<$5aXj{z3O7k2h$eAz2F2u-rn`X+#&!$CivvTI+KsK^)yH`&&%Au$mGD})S#(v=0!~1b",
        "s{KM2Vh_!0>eUOU&M-D!4ue9hgU<xK;aZR)#?Evev52S`3BZYyglF)0U5t%D`Xz_WFp!Mo@Y81;IfBc7u3cuDA1!5<b%9)P_~CWV&ke^m+G~zp4w6DTWab?@%Zg)3zS%pi9m*{@O;N6ChSQ<u^Jt1`wDqP!6s7o`(O1}fX{<o`KF)sMUUcbWVl6Q1t`ygpuKQfo-?bkb",
        "0vG9l&(_cU9CwIkAE_VQ>{$z%9g{xhf&d2}J3nynaN@Im^2}%7GjfL0&z#!E1N(RY9OGR5=qg1dEFk$}3dtdhJln~9C&w)K>zC)7n(}YYaw>lMWk&h}qRwZCCdqP8K+-7ubGnmk2Gf~Bu+4cR&XL{vT8vld@@M$$AJmNND*",
    )),
    "sub": (27, 29, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 ,.-'\u2019\u2014$%:", 230, (
        "c-obf!EW3(5Qax(V6Ks^>BM#_$Fdk8FR(=~GRjJ?VxTV|-_%+#85roPu&)OCDn8H%P+tP%+TLgs=&1)5z6hwW>QC+}-Z)O-a=sx}(vY0t47uAo+h+Uu^Re6c@c8W6`1s-lx~ES=H{H|QXiJlqFGrKuEl2E`?X6(4xjEX!5nEg6_V+(}j9-QLza1wsG?}cMCzHvO(5;*G",
        "$pjx_x3@ph6Cu7bJ82r<2_wi8b%6w25(A1@PCTbIAZbI87=X#RNx3Zmvvc9+((8`&oTMZvR={IUvLiWPyfKoG;I{}vFfi$fV_I(V0F_^mqK7Go@_-S{U<d{-*9|jU$$$$aAG3IgudoSAQx(_M16A;fjnE2xWc5vA0?bt0=mCV`l0R<jh_<91(Lii4;xss%C$_v7rtkso",
        "6tg7^LQodQe6Sd(-*@1F7{L%p9teLiN?UD_k^hunQ@P5a93CSSB&QZdqu*m07qd%pgXENCN^(ZBCh21lv?LYDGM0smITKc2dwu1xFO_+C%kHyC!)hj$BFza&+eh6CdUHv;quwe?N1a1YmfAv<qD+-^QVixKg|bewPLh?zN^7OFd(Q59n|3yBY}(qiv}tZrX;Wcw3IfdP",
        "Byd;BA#tuuoC^3)2%lg8GZ^1hav#sjy+gD(M`bK3_i#l$e%*0ttZVtXVRND;(vAmA8sc{4IGYusGx=EIi)7|^X8PLcE61JeR9mQ~XfSI<m6e`%aIqy-XLZ(OO;LGahrxiG8*>#&5XK`AU0^`jT>CsRj|2rHPKnRMP7UV{l+2Wj@`zj`vEXOo5%$}X#4jNi7*1I?oSt?V",
        "?MiNKzEml0tPnRwd>Qm_BQ9<YzqloS@elFtn3(?&dIBv8`9UBGno-!XYn)JAXe53j{wuL}#1=Pjyp7>6Yl)ZP2A)dFgeiobONT4>UL0~If_uKN!g~@uRYPDVX;#uq(W`d6`F+@9=1>9wVMxTyi>oZ|J%dZsXEoAWH0o0+koc@d#%*G`6}Ga+_O)f75!uTgHooZ^G!#rj",
        "HU5TNVsXLK22H2wbe8Ep$UQrsIAMi{(+w(D9je2oZYnP=zCf5?gG?c*-}Ezo2pRfej@co+=Y7=$nWYd4Qepl$8|swWSD3B#m6MjCdN)+25E=zJcDieuWwa`^yb+$eg_nl~Bt%i8TwH=kLM(^|@d!k;K{y{i?p}etD#}{MI8@iPjjH3Us*#;=*k`BeB80o#Y1LM}xP*7X",
        "jb>KQe7LBC4_R6q5`Gj~Yl=+;f73LjmG;4MrRibtLFqFsfrJyi+Z+@Jv+r=8rGal<f)o9<I#NFr2L-Zil4yx*vwC9=uFTO}I{Jg^KLba9(b2o^;P<}z<xGBiM&E#Q`W~Fo+cUa4OWyQ}>9E7ua?$YfUvm|?&H",
    )),
    "kick": (18, 20, "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 \u2022", 190, (
        "c-oaxPm9w~5FaUSBux|Rsms<x5IiRY+E<Lpf?s6If*yS#2YV>Ze2o1#PXs@M$G0qa&e7ZYn-|ljq6hPv3^RFe{`@8r%w{|b0;uT}Y9_Al56Zb=2<3TD7tiL0{<1rr&!M7dxZ)Co;d35c@u$P7`!;`ZtQMRV`Y-jAh{^MO_9FuLC2(mJP}$aMeWR_exH6edfyz`Sbyg-e",
        "dnU2PwIY3lqT)I+k*UbV=rLRjAseS8I9a{@r$5*!c@}kE^>v!A>9kh5&`B4KDpXz7jjQeVYIyehVEioiJ4!onFgdTOa>zL|nQ+smswXHC<|?LQka9&UC+iQCLw->HjWQ={Q2^y)4di$EUG_cw3GC9H8<$o}AE6XzSg#+KNrBABU`N#d8ABG+*quf4m`H*l)^2142u3^s",
        "Zn>qB9?hc(>2EmyVFC=gOKikeTZpz&XJan;iW8QV3F-a|-+$%pgGlp0%}2^V(;9<aQCU(9i78%^1aA=9heed|2B}<Dt4(b-{FW0+&e~~BYou+@c}x5U*#T)k2Bn5;-tyKsz-~Z4rVG3!9q0|LbHvo*&J#c~M(_*Txf&%-Ub_KF2NStt-gC<bnvmzZy`r2Nx^=a258q`&",
        "`<-tQ?P3@)s2pK5(&r6*!by$pYJ=X8TcV}9WbHWxV6^}%@Zsjjp>@0(bdZP#rp`yF?|ygRqIc{ymYneX0^7JV7X",
    )),
    "body": (20, 22, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.-'\u2019\u2014\u201c\u201d()$%:;!?/&", 405, (
        "c-nnc!EW0|5Pgb7QkG~@wtQgXK%^_cz69v1G7J{7O%)At@<&jqVdM~?0(!8E8rGnPBA?JxQS=Xb>3M?!K@R<Z9C~2UAMi0Z_wACDCCBc(<!EPTcXnoWcD26Vk<R*p1p!&RP1b5vqGg^(=6JoUj=x@MH#aM7w@c>xwznb06l=vYJH={yy{gytZ>O}S?fZcQtya~uV_uUz",
        "-|v=Vj$@d&bwzC@_Ih^3E$f!7*`#RgS;wumWsG*aWY&DE&3S8UR$OtnVE#R03+4a<$8qG5<J6_@x}JCqhl)mnY-@|6-PbbL-7HzVy&=KIhB4r9UxzC!>#VJr$;~QPE<9pg)+CfrcXgVlc@}4CqI8(bFjtw1`Q@poTop7M=Bf7bU=~6VSqalm(9gWwu2U+!12v*1)e04s",
        "`$l?Lr%=BRE*ATJ%)-pt48!QcyI$TU{kXd8Wuk8B(!WFDH8`9pJ(Lj+aEufq3`J>W0#~apth$<bU^`?Bu;0ePwrOAVFrtA0hX0zT{<N)`G!Kb`=7<=+QE$|H^-3i~=;i(EBvgLvXC-1^`AOKnHfbDbdQm|00G2%XzjgL3!n>=7V&gKBiexO+q4nWOO~Ya?bKK+|G#<bw",
        "M{1F%e(q_lCUHiJHFwdE#UMZcm(W^gxoOj1W%|1enQgWWY;L2^)<VAnpUnjg6szsZ4%&EZ{pK){O{k^3&GC-4Tw!kguSp$sN<L8(%M9~8!dQ5RsE_oFW~TaFAL|$e_T;F{Q(R{2NbgA?Cg0goai@%?5~FOKt2|qf%Ex(>1)M`q^;}nLj&vZMCrVx2mf-zMIeP*<)+z3D",
        "YY8zB-%_&)G*{?iRvC!(jtsDiXE<bK53nOU66<)C_I|<9ji`S_y%qJ9#GkbL-3S<&Ig>>Ynvp(`$%Q}YJQR9~y=Tl%;a7xnJI42f2U?Swobz(>u3pW`JSP2kH8Z6-ttWaaQ`zA~9$}N~Syy=b<JUiZ^X}!lm(O=k4qorSI!vA>VUpQvzinsq`8&i^XrQ!UbUi#NEfgh{",
        "Ajceci!8&O#WA*rPfSW^Q_5p03i+6a;NAmMoN;me#FVdFT4mwt2tP=1G3yecUiP8Clax8Bizkk(i@6{>^!Fy8=O$A%DV_?G@)U!`Ds#P4UiN;e{Z_tTc&l_oKj#ZSs*6-b8J2#Uh`yvRk%`sDIHs3IS4OUfd>T<+#?KkG;-fH$X9|}vWFCkZ6;YaKEYbWX$13ffou2%)",
        "kj~CtpS)j4VV7@rMKS+yV0lGGYoD!%|2n5Q#XkKB#M2Gkm^^1T%tHqxAr8AZQ+N^M#RO-6<Ma<4{f62A^#L9Y;C=@G7|o|pv%+<TQ*~h+nAnQ6g==(|xUnTt9cGsRzl5LbHu$e&T#FfcU=m4~m$HMgKm0lSkj=8$_(SCX2RDoOXa",
    )),
    "small": (15, 17, "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 ,.-'\u2019\u2014\u201c\u201d()$%:;!?/&", 405, (
        "c-oCpJCEB&5T28kyro1-gpq=U;9H!HgNrL@BZ%dIzN|#xa)yH-Ws2aidfY(<t{~t>Fa&9Tf=ZYEDRcs)cA4^iLP{3_oNtFq$&VD-4;;?UduOK8>DW%kk;sv57eva2@RdmrfQYcSuI*Uc>owXqb^#*h?$}REWYn0jmOYqbMa@ZRWfXO7_wcacSQdofqA2z<Ash+%8)%zr",
        "ug4yH5_=McxN^K8<V4^&XdE}3l(9F7cD4LpB8V&rA#6*CmTd(=V1srW3MTzNuAG;N2<~{|O6zj3gg{;)IyLDW9)g77uALOqH*}XC(|y{|#Exub*E9h)A^!)~)VCQKKm+cd(UH?zV@+i=P#Lyc8)MvO);rEPUj?6{(iQBgtm->2#-=hml**qn-JhgHmKj~s4J~Pf|CDAf",
        "Z*$gV29%3m7VmGi^X*kK1B@>9QZMveU+bx!=n0}9QRXV;VsUg<xfjgb8$s9nDu@5FJD>wgpIN&)TzAf3HSD!o;p!u$U%^zLLfJ?5h~C)|jS%CQPUt)Ien67`hzt3nym~X=o^Bt$AC{>}%?KGzpig1(EvyTA2NaM#V5#)jP>VuLQ9@Stc|&>FI-8Eqzpr1^)a~$!E@_}N",
        "ju{-dchNIw3vx9T;GWUoxY%f|?hTas;OFtB$pN*IG^Zx~t6g{pL(~i>Bg%G1-9j>*FP6)j>#5nF%fDxDX6YW6U&I?=HAf!zal8ENIs3tVU1g1*$~sT3bruV;ROSQU)o`C<#vZ?q&*u+Lhv}c{T>Y$Gn3wvgeuQ-$&+{}ry&l(kx0KoKO2{-*dX-}p#>m*<1bvY-q=&l!",
        ")o^w#KPopU9uqvBB*)hVLM(VlJ-Ua*IH7a;h?~P1zi;KO+R&_E<6``VbtwEg4G^)-@q}N81U5M=#`to?EO>o#uBG5E{op-@WZX)al5oILeYCco+x+7hy7=|49k=ydrkp!(mCEp`EK4wONF~a8O&7F4(jIkzHMb+P7xp<lzkTucNfIPcBHt!h4;RaghW}iUo0F3*V-cg@",
        "q?D9Ng3wx512pLv&r0c3kE@ZL*<Ak%6Nfc&",
    )),
}


def load_fonts():
    """Decode every table into {name: (size, ascent, {char: glyph})}."""
    fonts = {}
    for name, (size, ascent, charset, idx_len, lines) in TABLES.items():
        raw = zlib.decompress(base64.b85decode("".join(lines)))
        idx = raw[:idx_len]
        blob = raw[idx_len:]
        glyphs = {}
        off = 0
        for k, ch in enumerate(charset):
            adv, w, h, bx, top = idx[5 * k:5 * k + 5]
            stride = (w + 7) // 8
            glyphs[ch] = (adv, w, h, bx - 128, top, blob[off:off + stride * h])
            off += stride * h
        fonts[name] = (size, ascent, glyphs)
    return fonts


FONTS = load_fonts()


def glyph_width(font_name, text):
    _size, _asc, glyphs = FONTS[font_name]
    return sum(glyphs[ch][0] for ch in text if ch in glyphs)


def draw_text(text, font_name, x, baseline, color, align="left"):
    size, ascent, glyphs = FONTS[font_name]
    if align == "center":
        x -= glyph_width(font_name, text) // 2
    elif align == "right":
        x -= glyph_width(font_name, text)
    pen = x
    for ch in text:
        g = glyphs.get(ch)
        if g is None:
            continue
        adv, w, h, bx, top, bits = g
        if w and h:
            stride = (w + 7) // 8
            for yy in range(h):
                for xx in range(w):
                    if bits[yy * stride + xx // 8] & (0x80 >> (xx % 8)):
                        put(pen + bx + xx, baseline - top + yy, color)
        pen += adv
    return pen


def wrap(text, font_name, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if glyph_width(font_name, trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            # A single word wider than the column: hard-split it.
            while glyph_width(font_name, word) > max_w and len(word) > 1:
                cut = 1
                while cut < len(word) and glyph_width(font_name, word[:cut + 1]) <= max_w:
                    cut += 1
                lines.append(word[:cut])
                word = word[cut:]
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(text, font_name, x, top, max_w, leading, max_lines=None, color=INK):
    """Draw wrapped text; top is the top of the first line. Returns the
    y just below the last drawn line."""
    _size, ascent, _g = FONTS[font_name]
    lines = wrap(text, font_name, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        draw_text(line, font_name, x, top + ascent + i * leading, color)
    return top + ascent + (len(lines) - 1) * leading + 6


# ---- page content (Friday, 20 November 2026) ----
LEAD = (
    "APEC SUMMIT  \u2022  SHENZHEN",
    "TRUMP, XI AND PUTIN HOLD FIRST-EVER THREE-WAY TALKS",
    "Donald Trump, Xi Jinping and Vladimir Putin held 90 minutes of "
    "three-way talks on the sidelines of APEC \u2014 the first such meeting. "
    "A joint statement pledged UN reform, lower nuclear risk and higher oil "
    "output, but no breakthrough on Ukraine or Iran.",
)

STORIES = [
    ("THE HAGUE",
     "COURT FINDS MYANMAR GUILTY OF GENOCIDE",
     "The International Court of Justice ruled Myanmar committed genocide "
     "against the Rohingya in 2017 \u2014 the first ruling of its kind \u2014 "
     "and ordered reparations."),
    ("MARKETS",
     "ANTHROPIC IPO IS THE BIGGEST EVER",
     "Anthropic priced its shares at $83 and raised $81.3 billion, the "
     "largest offering in history. The stock jumped 34% at its Nasdaq debut "
     "before easing back."),
    ("INDIA",
     "CYCLONE AKVAN STRIKES ODISHA COAST",
     "Cyclone Akvan came ashore near Gopalpur, Odisha, around noon. Some "
     "300,000 people were evacuated, 423 rescue teams deployed and 69 trains "
     "cancelled."),
    ("SAUDI ARABIA",
     "HOUTHI STRIKE HITS RIYADH\u2019S PIF TOWER",
     "A Houthi attack damaged the Public Investment Fund tower in Riyadh, "
     "shattering windows across seven floors. No one was hurt."),
    ("WASHINGTON",
     "TRUMP IN NO RUSH ON IRAN \u2014 DECISION WAITS UNTIL 2027",
     "Donald Trump said there was no hurry over Iran and that he would "
     "decide after 1 January, pushing any decision into 2027."),
]

BAND_ITEMS = [
    ("VOYAGER 1",
     "NASA confirms Voyager 1 is one light-day from Earth \u2014 a first for "
     "a human-made object."),
    ("UKRAINE",
     "European leaders say they are ready to negotiate with Russia to end "
     "the war in Ukraine."),
]

FOOTER = "Every story above was first reported on Friday, 20 November 2026."

MX = 40
RX = 984
CW = RX - MX


def draw_story(x, w, kicker, headline, body_text, body_font, body_leading,
               body_lines, y):
    """One story block; returns the y just below it."""
    draw_text(kicker, "kick", x, y + 18, GOLD)
    hb = draw_para(headline, "sub", x, y + 26, w, 31, color=INK)
    bb = draw_para(body_text, body_font, x, hb + 8, w, body_leading,
                   max_lines=body_lines, color=SOFT)
    return bb


def build_page():
    # ---- masthead ----
    hline(MX, RX, 26, 3, INK)
    hline(MX, RX, 32, 1, INK)
    draw_text("THE WORLD TODAY", "mast", W // 2, 111, INK, align="center")
    globe(928, 92, 30, INK)
    draw_text("FRIDAY, 20 NOVEMBER 2026", "small", W // 2, 145, SOFT,
              align="center")
    hline(MX, RX, 160, 4, INK)
    hline(MX, RX, 167, 1, INK)

    # ---- lead story ----
    draw_text(LEAD[0], "kick", MX, 196, GOLD)
    hb = draw_para(LEAD[1], "head", MX, 206, CW, 40, color=INK)
    y = draw_para(LEAD[2], "body", MX, hb + 10, CW, 25, color=INK)
    y += 10
    hline(MX, RX, y, 2, INK)
    grid_top = y + 10

    # ---- stories grid: two columns, two rows, then a full-width row ----
    col_w = (CW - 24) // 2
    left_x = MX
    right_x = MX + col_w + 24
    row1 = max(
        draw_story(left_x, col_w, *STORIES[0], "small", 19, 3, grid_top),
        draw_story(right_x, col_w, *STORIES[1], "small", 19, 3, grid_top),
    )
    row2_top = row1 + 10
    row2 = max(
        draw_story(left_x, col_w, *STORIES[2], "small", 19, 3, row2_top),
        draw_story(right_x, col_w, *STORIES[3], "small", 19, 3, row2_top),
    )
    vline(MX + col_w + 12, grid_top, row2, 1, (198, 192, 180))
    y = draw_story(MX, CW, *STORIES[4], "body", 25, 2, row2 + 10)
    y += 8
    hline(MX, RX, y, 1, INK)

    # ---- ALSO TODAY band ----
    band_top = y + 10
    band_h = 96
    fill_rect(MX, band_top, CW, band_h, INK)
    draw_text("ALSO TODAY", "kick", MX + 18, band_top + 48, GOLD)
    for i, (label, text) in enumerate(BAND_ITEMS):
        bx = MX + 200 + i * 400
        bw = 372 if i == 0 else 326
        draw_text(label, "kick", bx, band_top + 24, WHITE)
        draw_para(text, "small", bx, band_top + 30, bw, 19,
                  max_lines=3, color=WHITE)
    band_bottom = band_top + band_h

    # ---- footer ----
    draw_text(FOOTER, "small", W // 2, band_bottom + 20, SOFT, align="center")
    final_y = band_bottom + 24
    assert final_y <= 1020, "page overflow: final_y=%d" % final_y
    return final_y


def png_bytes():
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw += CANVAS[yy * W * 3:(yy + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    final_y = build_page()
    data = png_bytes()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else os.getcwd()
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s %d bytes final_y=%d" % (path, len(data), final_y))


if __name__ == "__main__":
    main()
