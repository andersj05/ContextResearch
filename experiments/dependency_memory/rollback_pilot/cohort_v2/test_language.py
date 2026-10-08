"""Check that the execution language correction is public and cohort-wide."""
import unittest

from ..cohort_v1.authored import generate as original
from ..math_tasks import generate_math
from ..subscription.profile import Renderer
from .authored import generate, LANGUAGE


class LanguageAmendmentTests(unittest.TestCase):
    def test_language_is_public_and_every_problem_test_and_reference_is_retained(self):
        before,after=original(),generate()
        self.assertEqual(len(after),12)
        for (old,oe),(new,ne) in zip(before,after,strict=True):
            self.assertEqual(old.task_id,new.task_id)
            self.assertEqual(old.stratum,new.stratum)
            public=new.data()
            self.assertTrue(public["statement"].startswith(LANGUAGE))
            self.assertIn("Python 3.11",Renderer().render("checkpoint",new).json_text)
            public["statement"]=public["statement"][len(LANGUAGE):]
            self.assertEqual(public,old.data())
            private=ne.data();private.pop("language_amendment")
            self.assertEqual(private,oe.data())
            ne.check_binding(new)

    def test_schedule_order_matches_original_and_independent_math_hashes_are_identical(self):
        from ..cohort_v1.run import cohort as first
        from .run import cohort as second
        a,b=first(),second()
        self.assertEqual([t.task_id for t,e in a],[t.task_id for t,e in b])
        self.assertEqual({t.task_id:t.hash for t,e in b if t.domain=="math"},{t.task_id:t.hash for t,e in generate_math()})


if __name__=="__main__":unittest.main()
