# Key Concepts in Oppia #

An Oppia exploration is meant to simulate a one-on-one conversation between a tutor and a student. Here is an example of such a conversation:

  * **Tutor**: Let's say you had a red ball, a blue ball and a yellow ball. How many different color arrangements can you get if you put them in a straight line?
  * **Student**: (thinks) There are four ways.
  * **Tutor**: OK, what are they?
  * **Student**: Well, you can put the red ball on the left, the blue ball in the middle, and the yellow ball on the right -- so, Red-Blue-Yellow. There's also Blue-Red-Yellow, Blue-Yellow-Red, and Red-Blue-Yellow. That's four ways.
  * **Tutor**: I think you've counted one of them twice...
  * **Student**: Oops, oh yes. There's an extra Red-Blue-Yellow. So, there's three ways.
  * **Tutor**: Well, let's check that we haven't missed any. Let's say the red ball is on the left. Have you found all the possibilities in that case?
  * **Student**: Well, there's Red-Blue-Yellow -- oh, and Red-Yellow-Blue. Oh, and also Yellow-Blue-Red. And Yellow-Red-Blue. (Pause.) I think that's all.
  * **Tutor**: OK, are you sure we haven't missed any?
  * **Student**: Well, I found all the ways with the Red ball on the left -- and all the ways with the Blue ball on the left, and all the ways with the Yellow ball on the left. So I think that's all.
  * **Tutor**: Yes, that's great. It's important to work systematically and do this sort of thing in an orderly way, otherwise you'll probably miss something. By the way, it looks like there are two arrangements for each of the three cases you mention; I wonder why that is...? (1)

Notice that this conversation involves the student to a large degree, and that the tutor is trying to understand the student's answers and provide appropriate feedback that will help the student to get a better understanding of what's going on.

In Oppia, such a conversation is modelled as a series of **states**. Each state is made up of a 'tutor' part (the **content**) and a 'student' part (the **interaction**).

For example, here is a screenshot of the learner view of an exploration that models the first part of the above conversation:

> <img src='http://wiki.oppia.googlecode.com/git/images/three_balls.png' width='500'></li></ul>

The tutor presents a question with a picture (the 'content'), and offers, as the 'interaction', an input field that allows the student to type in a number.<br>
<br>
Based on the student's response, the tutor may decide to do different things:<br>
<br>
<ul><li>If the answer is 6, they may immediately move to a harder follow-up question, such as the case of four balls.<br>
</li><li>If the answer is less than 6, they may ask the student to enumerate the cases, in the hope that the error will become clearer.<br>
</li><li>If the answer is obviously too small or obviously too large, they may point that out, in order to help the student learn how to do 'sanity checks'.</li></ul>

and so on. These choices are called <b>rules</b>. As responses from students come in, the rules can be edited, and new rules added -- there's no need to determine all the possible rules at the outset. Note that all this complexity is effectively hidden from the learner, since each learner playthrough resembles a linear conversation. The following screenshot shows what two different playthroughs of the same exploration look like, when placed side-by-side:<br>
<br>
<blockquote><img src='http://wiki.oppia.googlecode.com/git/images/three_balls_side_by_side.png' width='900'></blockquote>

To summarize:

  * The learning units in Oppia are called **explorations**.
  * Each exploration is divided up into **states**.
  * Each state consists of some (non-interactive) **content** and an **interaction** which accepts a student's response.
  * Based on the response, Oppia determines what to say next based on a set of **rules**.

Note that Oppia also comes packaged with additional features (such as parameters) that allow further personalization of an exploration. Read on to find out more!

_Next: [The exploration gallery](TheExplorationGallery.md)_


---


(1) Note the difference between this conversation and the following two conversations:

  * **Tutor**: Let's say you had a red ball, a blue ball and a yellow ball. How many different color arrangements can you get if you put them in a straight line?
  * **Student**: (thinks) There are four ways.
  * **Tutor**: Wrong. Try again.
  * **Student**: (thinks) There are five ways.
  * **Tutor**: Wrong. Try again.

and

  * **Tutor**: Let's say you had a red ball, a blue ball and a yellow ball. How many different color arrangements can you get if you put them in a straight line?
  * **Student**: (thinks) There are four ways.
  * **Tutor**: No, there are six ways. This is because there are three ways to pick the ball in the first position. For each of these three ways there are two ways to pick the ball in the second position. After that, the final ball is fixed. So there are 3 x 2 x 1 ways, which is 6 ways. Do you understand?
  * **Student**: ...