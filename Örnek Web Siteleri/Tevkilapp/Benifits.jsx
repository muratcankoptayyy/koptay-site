import BeniftContent from "./BeniftContent";

const Benifits = () => {
  return (
    <>
      {/* <!-- Benefits --> */}
      <section className="py-24 dark:bg-jacarta-900">
        <div className="container">
          <div className="mx-auto mb-16 max-w-xl text-center">
            <h2 className="mb-6 text-center font-display text-3xl font-medium text-jacarta-700 dark:text-white">
              Neden TevkilApp&apos;i Tercih Etmelisiniz?
            </h2>
            <p className="text-lg dark:text-jacarta-300">
              Çünkü TevkilApp, sizin için adil ve güvenli bir şekilde tüm tevkil işlemlerinizi yeni teknolojilerle tüm cihazlarınızda en hızlı şekilde yapmanızı sağlar.
            </p>
          </div>
          <BeniftContent />
        </div>
      </section>
      {/* <!-- end benefits --> */}
    </>
  );
};

export default Benifits;
