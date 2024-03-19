class DateInfor:
      def __init__(self,start_index, max_res, page_num, datetime, updated_max) -> None:
            self.start_index = start_index
            self.datetime = datetime
            self.max_results = max_res
            self.page_num = page_num
            self.updated_max = updated_max

      def to_dict(self):
            return {
                'start_index': self.start_index,
                'max_results': self.max_results,
                'page_num': self.page_num,
                'datetime': self.datetime,
                'updated_max': self.updated_max
            }